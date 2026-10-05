"""Bounded static-mesh reconstruction candidate; run with Blender --python.

No provider calls, installation, source overwrite, automatic retry or validated
claim. Use --help for the interface and reconstruction-report.json for results.
"""
import argparse
import datetime
import hashlib
import json
import math
from pathlib import Path
import sys
import uuid


def polygon_range(target, tolerance=.2):
    if target < 4 or not 0 <= tolerance <= .2:
        raise ValueError('Target must be >=4; tolerance must be between 0 and 0.2')
    return math.ceil(target * (1-tolerance)), math.floor(target * (1+tolerance))


def allocate_budget(weights, target):
    if not weights or any(w <= 0 for w in weights) or target < 24*len(weights):
        raise ValueError('Need positive mesh areas and at least 24 faces per mesh')
    remaining = target-24*len(weights)
    shares = [remaining*w/sum(weights) for w in weights]
    result = [24+int(x) for x in shares]
    for i in sorted(range(len(weights)), key=lambda i: shares[i] % 1, reverse=True)[:target-sum(result)]:
        result[i] += 1
    return result


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def topology(obj):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    remaining = set(bm.verts); components = []
    while remaining:
        start = remaining.pop(); todo = [start]; verts = [start]
        while todo:
            for edge in todo.pop().link_edges:
                for v in edge.verts:
                    if v in remaining:
                        remaining.remove(v); todo.append(v); verts.append(v)
        components.append([max(v.co[i] for v in verts)-min(v.co[i] for v in verts) for i in range(3)])
    result = dict(faces=len(bm.faces), quads=sum(len(f.verts)==4 for f in bm.faces),
                  triangles=sum(len(f.verts)-2 for f in bm.faces),
                  boundary_edges=sum(e.is_boundary for e in bm.edges),
                  nonmanifold_edges=sum(not e.is_manifold for e in bm.edges),
                  components=len(components), component_extents=components)
    bm.free(); return result


def bounds(objects):
    points = [o.matrix_world@v.co for o in objects for v in o.data.vertices]
    return [min(p[i] for p in points) for i in range(3)], [max(p[i] for p in points) for i in range(3)]


def surface_error(source, target):
    from mathutils.bvhtree import BVHTree
    def tree(o):
        m=o.data; m.calc_loop_triangles()
        return BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],
                                   [tuple(t.vertices) for t in m.loop_triangles], all_triangles=True)
    def probe(a,b):
        t=tree(b); points=[a.matrix_world@v.co for v in a.data.vertices]
        points += [a.matrix_world@p.center for p in a.data.polygons]
        return max(t.find_nearest(p)[3] for p in points)
    return max(probe(source,target),probe(target,source))


def select(*objects):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects: o.select_set(True)
    bpy.context.view_layer.objects.active=objects[-1]


def extend_atlas(pixels, coverage):
    """Deterministic nearest-seed approximation (jump flood); preserve RGBA seeds."""
    import numpy as np
    h,w=coverage.shape
    if not coverage.any(): raise ValueError('EMPTY_UV_COVERAGE')
    yy,xx=np.indices((h,w),dtype=np.int32)
    sy=np.where(coverage,yy,-1);sx=np.where(coverage,xx,-1)
    step=1
    while step<max(h,w):step*=2
    while step>=1:
        distance=np.where(sy>=0,(sy-yy)**2+(sx-xx)**2,np.iinfo(np.int32).max)
        for dy in (-step,0,step):
            for dx in (-step,0,step):
                if not (dy or dx):continue
                y0=max(0,-dy);y1=min(h,h-dy);x0=max(0,-dx);x1=min(w,w-dx)
                if y0>=y1 or x0>=x1:continue
                cy=sy[y0+dy:y1+dy,x0+dx:x1+dx].copy()
                cx=sx[y0+dy:y1+dy,x0+dx:x1+dx].copy()
                d=(cy-yy[y0:y1,x0:x1])**2+(cx-xx[y0:y1,x0:x1])**2
                better=(cy>=0)&(d<distance[y0:y1,x0:x1])
                sy[y0:y1,x0:x1][better]=cy[better];sx[y0:y1,x0:x1][better]=cx[better]
                distance[y0:y1,x0:x1][better]=d[better]
        step//=2
    if (sy<0).any():raise ValueError('INCOMPLETE_PADDING')
    result=pixels.copy();outside=~coverage
    result[outside]=pixels[sy[outside],sx[outside]]
    return result


def bake_coverage(target, mat, size):
    """Bake target UV coverage without source projection or color heuristics."""
    import numpy as np
    scene=bpy.context.scene
    image=bpy.data.images.new('PaddingCoverage',width=size,height=size,alpha=False)
    image.colorspace_settings.name='Non-Color'
    node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image
    output=mat.node_tree.nodes.get('Material Output');old=output.inputs['Surface'].links[0].from_socket
    emission=mat.node_tree.nodes.new('ShaderNodeEmission');emission.inputs['Color'].default_value=(1,1,1,1)
    mat.node_tree.links.new(emission.outputs[0],output.inputs['Surface'])
    mat.node_tree.nodes.active=node;select(target)
    scene.render.bake.use_selected_to_active=False;scene.render.bake.margin=0
    try:
        bpy.ops.object.bake(type='EMIT')
        data=np.empty(size*size*4,dtype=np.float32);image.pixels.foreach_get(data)
        return data.reshape(size,size,4)[:,:,0]>.5
    finally:
        mat.node_tree.links.new(old,output.inputs['Surface'])
        mat.node_tree.nodes.remove(node);mat.node_tree.nodes.remove(emission);bpy.data.images.remove(image)
        scene.render.bake.use_selected_to_active=True;scene.render.bake.margin=16


def bake(source, target, out, size, ray):
    mats=[]
    for slot in source.material_slots:
        if slot.material is None: raise ValueError('EMPTY_SOURCE_MATERIAL_SLOT')
        slot.material=slot.material.copy(); m=slot.material
        nodes=m.node_tree.nodes if m.use_nodes else []
        bs=[n for n in nodes if n.type=='BSDF_PRINCIPLED']
        outputs=[n for n in nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output]
        if len(bs)!=1 or len(outputs)!=1: raise ValueError('UNSUPPORTED_SOURCE_MATERIAL')
        surface=outputs[0].inputs['Surface']
        if not surface.is_linked or surface.links[0].from_node!=bs[0]:
            raise ValueError('SOURCE_SURFACE_MUST_BE_DIRECT_PRINCIPLED')
        if bs[0].inputs['Alpha'].is_linked or bs[0].inputs['Alpha'].default_value < .999:
            raise ValueError('TRANSPARENT_SOURCE_UNSUPPORTED')
        mats.append((m,bs[0],outputs[0],m.node_tree.nodes.new('ShaderNodeEmission')))
    if not mats: raise ValueError('SOURCE_MATERIAL_REQUIRED')
    mat=bpy.data.materials.new(target.name+'_PBR');mat.use_nodes=True
    target.data.materials.clear();target.data.materials.append(mat)
    for p in target.data.polygons:p.material_index=0;p.use_smooth=True
    bs=mat.node_tree.nodes.get('Principled BSDF');images={}
    select(source,target)
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16
    scene.render.bake.use_selected_to_active=True;scene.render.bake.cage_extrusion=ray
    scene.render.bake.max_ray_distance=ray*2;scene.render.bake.margin=16
    coverage=bake_coverage(target,mat,size)
    select(source,target)
    import numpy as np
    for name,socket in [('BaseColor','Base Color'),('Roughness','Roughness'),('Metallic','Metallic'),('Normal',None)]:
        image=bpy.data.images.new(target.name+'_'+name,width=size,height=size,alpha=False)
        image.colorspace_settings.name='sRGB' if name=='BaseColor' else 'Non-Color'
        node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;mat.node_tree.nodes.active=node
        for m,sb,output,em in mats:
            if socket is None:m.node_tree.links.new(sb.outputs['BSDF'],output.inputs['Surface'])
            else:
                for link in list(em.inputs['Color'].links):m.node_tree.links.remove(link)
                inp=sb.inputs[socket]
                if inp.is_linked:m.node_tree.links.new(inp.links[0].from_socket,em.inputs['Color'])
                else:
                    v=inp.default_value;em.inputs['Color'].default_value=tuple(v) if hasattr(v,'__len__') else (v,v,v,1)
                m.node_tree.links.new(em.outputs[0],output.inputs['Surface'])
        bpy.ops.object.bake(type='NORMAL' if socket is None else 'EMIT',normal_space='TANGENT')
        values=np.empty(size*size*4,dtype=np.float32);image.pixels.foreach_get(values)
        padded=extend_atlas(values.reshape(size,size,4),coverage)
        image.pixels.foreach_set(padded.ravel());image.update()
        image.filepath_raw=str(out/(target.name+'_'+name+'.png'));image.file_format='PNG';image.save();images[name]=node
    for m,sb,output,em in mats:m.node_tree.links.new(sb.outputs['BSDF'],output.inputs['Surface']);m.node_tree.nodes.remove(em)
    for name,socket in [('BaseColor','Base Color'),('Roughness','Roughness'),('Metallic','Metallic')]:
        mat.node_tree.links.new(images[name].outputs['Color'],bs.inputs[socket])
    normal=mat.node_tree.nodes.new('ShaderNodeNormalMap')
    mat.node_tree.links.new(images['Normal'].outputs['Color'],normal.inputs['Color'])
    mat.node_tree.links.new(normal.outputs[0],bs.inputs['Normal'])


def previews(sources, targets, out):
    from mathutils import Vector
    scene=bpy.context.scene;lo,hi=bounds(sources);center=(Vector(lo)+Vector(hi))/2;size=max(Vector(hi)-Vector(lo))
    scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
    scene.render.resolution_x=960;scene.render.resolution_y=720;scene.render.resolution_percentage=100
    scene.world=bpy.data.worlds.new('ReconstructionReview');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.4
    cam=bpy.data.cameras.new('ReviewCamera');co=bpy.data.objects.new(cam.name,cam);scene.collection.objects.link(co)
    scene.camera=co;cam.type='ORTHO';cam.ortho_scale=size*1.4;cam.clip_end=max(100,size*20);cam.clip_start=max(.0001,size*.0001)
    for i,(d,energy) in enumerate([((1,-2,3),200),((-2,-1,2),150),((0,2,3),180)]):
        light=bpy.data.lights.new('ReviewLight'+str(i),'AREA');light.energy=energy*size*size;light.size=size*2
        ob=bpy.data.objects.new(light.name,light);scene.collection.objects.link(ob);ob.location=center+Vector(d)*size
        ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler()
    for label,visible,hidden in [('before',sources,targets),('after',targets,sources)]:
        for o in visible:o.hide_render=False
        for o in hidden:o.hide_render=True
        for direction,vec in [('front',(1,-2,1)),('back',(-1,2,1)),('bottom',(1,-2,-1))]:
            co.location=center+Vector(vec)*size;co.rotation_euler=(center-co.location).to_track_quat('-Z','Y').to_euler()
            scene.render.filepath=str(out/(label+'_'+direction+'.png'));bpy.ops.render.render(write_still=True)


def run(args, report):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    suffix=args.input_file.suffix.lower()
    if suffix=='.blend':bpy.ops.wm.open_mainfile(filepath=str(args.input_file))
    elif suffix=='.fbx':bpy.ops.import_scene.fbx(filepath=str(args.input_file))
    elif suffix in {'.glb','.gltf'}:bpy.ops.import_scene.gltf(filepath=str(args.input_file))
    else:raise ValueError('Expected blend/fbx/glb/gltf')
    all_meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    originals=[o for o in all_meshes if not args.object or o.name in args.object]
    if not originals or (args.object and set(args.object)-{o.name for o in originals}):raise ValueError('MESH_SELECTION_MISSING')
    units=1 if suffix in {'.glb','.gltf'} else args.meters_per_unit
    if units is None:
        if bpy.context.scene.unit_settings.system!='METRIC':raise ValueError('METERS_PER_UNIT_REQUIRED')
        units=bpy.context.scene.unit_settings.scale_length
    if units<=0 or not math.isfinite(units):raise ValueError('INVALID_UNITS')
    if any(o.data.shape_keys or o.find_armature() or o.animation_data or any(m.type=='ARMATURE' for m in o.modifiers) for o in originals):
        raise ValueError('STATIC_MESHES_ONLY')
    original_names=[o.name for o in originals]
    sources=[]
    for i,o in enumerate(originals):
        mesh=bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        mesh.transform(o.matrix_world)
        for v in mesh.vertices:v.co*=units
        source=bpy.data.objects.new('Source_'+str(i),mesh);bpy.context.scene.collection.objects.link(source);sources.append(source)
    for o in list(bpy.context.scene.objects):
        if o not in sources:bpy.data.objects.remove(o,do_unlink=True)
    bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
    budgets=allocate_budget([sum(p.area for p in o.data.polygons) for o in sources],args.target_faces)
    targets=[]
    for index,(source,budget) in enumerate(zip(sources,budgets)):
        report['stage']='remesh_'+str(index)
        target=source.copy();target.data=source.data.copy();bpy.context.collection.objects.link(target);target.name='Reconstructed_'+str(index)
        targets.append(target);before=topology(target)
        if any(min(ext)<4*args.voxel_size_m for ext in before['component_extents']):raise ValueError('THIN_COMPONENT_USE_SMALLER_VOXEL_OR_LOCAL_REPAIR')
        select(target);target.data.remesh_voxel_size=args.voxel_size_m;bpy.ops.object.voxel_remesh()
        bm=bmesh.new();bm.from_mesh(target.data)
        # QuadriFlow rejects near-zero edges. Clean only the intermediate mesh.
        cleanup=min(args.voxel_size_m*.02, .0002)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=cleanup)
        bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=cleanup)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(target.data);bm.free();target.data.update()
        bpy.ops.object.quadriflow_remesh(use_mesh_symmetry=False,use_preserve_sharp=False,use_preserve_boundary=False,
            smooth_normals=True,mode='FACES',target_faces=budget,seed=args.seed)
        after=topology(target);report['meshes'].append({'source':original_names[index],'before':before,'after':after})
        if after['components']!=before['components']:raise ValueError('COMPONENT_COUNT_CHANGED')
        if after['nonmanifold_edges'] or after['quads']!=after['faces']:raise ValueError('RECONSTRUCTION_TOPOLOGY_FAILED')
        error=surface_error(source,target);report['meshes'][-1]['sampled_surface_error_m']=error
        if error>args.max_surface_error_m:raise ValueError('SURFACE_DISPLACEMENT_EXCEEDED')
        a,b=bounds([source]),bounds([target])
        if max(abs(a[j][i]-b[j][i]) for j in range(2) for i in range(3))>args.max_surface_error_m:raise ValueError('BOUNDS_CHANGED')
    count=sum(len(o.data.polygons) for o in targets);lo,hi=polygon_range(args.target_faces,args.tolerance)
    if not lo<=count<=hi:raise ValueError('FACE_BUDGET_FAILED')
    for index,(source,target) in enumerate(zip(sources,targets)):
        report['stage']='bake_'+str(index)
        select(target);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.008,correct_aspect=True);bpy.ops.object.mode_set(mode='OBJECT')
        for o in sources+targets:o.hide_render=o not in (source,target)
        bake(source,target,args.output_dir,args.texture_size,args.max_surface_error_m*1.5)
    report['stage']='visual_candidates';previews(sources,targets,args.output_dir)
    for source in sources:bpy.data.objects.remove(source,do_unlink=True)
    select(*targets);bpy.ops.file.pack_all();bpy.context.scene.render.engine='BLENDER_EEVEE'
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.shading.type='MATERIAL'
    bpy.ops.export_scene.fbx(filepath=str(args.output_dir/'candidate.fbx'),use_selection=True,object_types={'MESH'},
        add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True,axis_forward='-Z',axis_up='Y')
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output_dir/'candidate.blend'))
    report.update(stage='candidate_ready',status='prototype',faces=count,
        remaining_gates=['Visual before/after review','Self-intersection, UV overlap and padding','Source audit and clean exchange comparison','Authorized engine audit and receipt'])
    report['outputs']=[{'path':str(p),'sha256':sha(p)} for p in sorted(args.output_dir.iterdir()) if p.is_file()]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-file',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--object',action='append');parser.add_argument('--target-faces',type=int,required=True)
    parser.add_argument('--voxel-size-m',type=float,required=True);parser.add_argument('--meters-per-unit',type=float)
    parser.add_argument('--max-surface-error-m',type=float);parser.add_argument('--tolerance',type=float,default=.2)
    parser.add_argument('--texture-size',type=int,choices=[256,512,1024,2048,4096],default=2048);parser.add_argument('--seed',type=int,default=7)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:])
    polygon_range(args.target_faces,args.tolerance)
    if not math.isfinite(args.voxel_size_m) or args.voxel_size_m<=0:parser.error('voxel size must be positive and finite')
    args.max_surface_error_m=args.max_surface_error_m if args.max_surface_error_m is not None else args.voxel_size_m*4
    if not math.isfinite(args.max_surface_error_m) or args.max_surface_error_m<=0:parser.error('surface error must be positive and finite')
    args.input_file=args.input_file.resolve(strict=True);args.output_dir=args.output_dir.resolve()
    args.output_dir.mkdir(parents=True,exist_ok=False)
    report={'schema_version':'1.0','run_id':str(uuid.uuid4()),'status':'failed','stage':'load','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'input':{'path':str(args.input_file),'sha256':sha(args.input_file)},'parameters':{k:str(v) if isinstance(v,Path) else v for k,v in vars(args).items()},'meshes':[]}
    global bpy,bmesh
    import bpy,bmesh
    report['blender_version']=bpy.app.version_string;report['implementation_sha256']=sha(Path(__file__))
    try:run(args,report)
    except Exception as exc:report['error']=str(exc);raise
    finally:
        report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        (args.output_dir/'reconstruction-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print('AUTO_TA_RECONSTRUCT='+json.dumps({k:report[k] for k in ['status','stage','run_id']}))


if __name__=='__main__':main()
