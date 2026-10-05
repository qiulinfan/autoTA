"""Opt-in real Blender smoke tests: set AUTOTA_TEST_BLENDER to the executable."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
BLENDER=os.environ.get('AUTOTA_TEST_BLENDER')
SCRIPT=ROOT/'skills/auto-ta/scripts/blender_reconstruct.py'

@unittest.skipUnless(BLENDER,'Set AUTOTA_TEST_BLENDER for real DCC tests')
class BlenderReconstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='autota-reconstruct-')
        cls.folder=Path(cls.tmp.name)
        fixture=cls.folder/'fixture.py'
        fixture.write_text('''import bpy,sys
from pathlib import Path
root=Path(sys.argv[sys.argv.index('--')+1])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object;o.name='Prop';o.scale=(1,.5,.5)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
mod=o.modifiers.new('Rounded','BEVEL');mod.width=.1;mod.segments=3
bpy.ops.object.modifier_apply(modifier=mod.name)
mat=bpy.data.materials.new('SourcePBR');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.65,.025,.01,1);bs.inputs['Roughness'].default_value=.6
image=bpy.data.images.new('CheckerSource',width=32,height=32)
pixels=[]
for y in range(32):
 for x in range(32):pixels.extend((.8,.03,.01,1) if ((x//8+y//8)%2) else (.02,.03,.8,1))
image.pixels.foreach_set(pixels);image.pack()
texture=mat.node_tree.nodes.new('ShaderNodeTexImage');texture.image=image
mat.node_tree.links.new(texture.outputs['Color'],bs.inputs['Base Color'])
o.data.materials.append(mat)
bpy.context.scene.unit_settings.system='METRIC'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'source.blend'))
o.scale.z=.001
bpy.ops.wm.save_as_mainfile(filepath=str(root/'thin.blend'))
''',encoding='utf-8')
        result=cls.invoke(fixture,[str(cls.folder)])
        if result.returncode:raise RuntimeError(result.stdout[-4000:])

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    @staticmethod
    def invoke(script,args):
        return subprocess.run([BLENDER,'--background','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','1','--python',str(script),'--',*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',timeout=180)

    def arguments(self,input_name,output):
        return ['--input-file',str(self.folder/input_name),'--output-dir',str(output),'--target-faces','500','--voxel-size-m','.025','--max-surface-error-m','.1','--texture-size','256']

    def test_padding_preserves_seeds_and_fills_2k(self):
        probe=self.folder/'padding_probe.py'
        probe.write_text("""import importlib.util, numpy as np
spec=importlib.util.spec_from_file_location('reconstruct',"""+repr(str(SCRIPT))+""")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
a=np.zeros((2048,2048,4),dtype=np.float32)
mask=np.zeros((2048,2048),dtype=bool)
mask[100:200,100:200]=True;mask[1700:1800,1700:1800]=True
a[100:200,100:200]=(0,0,0,.25)
a[1700:1800,1700:1800]=(.7,.2,.1,1)
b=m.extend_atlas(a,mask)
assert np.array_equal(a[mask],b[mask])
assert np.all((b[:,:,3]==.25)|(b[:,:,3]==1))
assert np.array_equal(b[0,0],a[100,100])
assert np.array_equal(b[-1,-1],a[1700,1700])
assert np.array_equal(m.extend_atlas(a,np.ones_like(mask)),a)
try:m.extend_atlas(a,np.zeros_like(mask))
except ValueError:pass
else:raise AssertionError('empty coverage accepted')
print('PADDING_2K_OK')
""",encoding='utf-8')
        result=self.invoke(probe,[])
        self.assertEqual(result.returncode,0,result.stdout[-4000:])
        self.assertIn('PADDING_2K_OK',result.stdout)

    def test_full_candidate_and_no_overwrite(self):
        output=self.folder/'success';source=self.folder/'source.blend';original=hashlib.sha256(source.read_bytes()).hexdigest()
        args=self.arguments('source.blend',output);result=self.invoke(SCRIPT,args)
        self.assertEqual(result.returncode,0,result.stdout[-5000:])
        report=json.loads((output/'reconstruction-report.json').read_text())
        self.assertEqual(report['status'],'prototype');self.assertTrue(400<=report['faces']<=600)
        self.assertTrue(all(x['after']['nonmanifold_edges']==0 for x in report['meshes']))
        self.assertTrue((output/'candidate.blend').is_file());self.assertTrue((output/'candidate.fbx').is_file())
        self.assertEqual(len(list(output.glob('Reconstructed_0_*.png'))),4)
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),original)
        probe=self.folder/'probe.py'
        probe.write_text('''import bpy,sys
from pathlib import Path
p=Path(sys.argv[sys.argv.index('--')+1])
bpy.ops.wm.open_mainfile(filepath=str(p/'candidate.blend'))
o=next(o for o in bpy.context.scene.objects if o.type=='MESH')
count=len(o.data.polygons)
assert all(len(f.vertices)==4 for f in o.data.polygons)
image=bpy.data.images.load(str(p/'Reconstructed_0_BaseColor.png'),check_existing=False)
px=list(image.pixels);red=px[0::4];blue=px[2::4]
assert max(red)>.2 and max(blue)>.2, 'Source checker colors were not baked'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(p/'candidate.fbx'))
o=next(o for o in bpy.context.scene.objects if o.type=='MESH')
assert len(o.data.polygons)==count
assert len(o.data.uv_layers)>0 and len(o.data.materials)>0
''',encoding='utf-8')
        checked=self.invoke(probe,[str(output)])
        self.assertEqual(checked.returncode,0,checked.stdout[-5000:])
        receipt=(output/'reconstruction-report.json').read_bytes()
        again=self.invoke(SCRIPT,args);self.assertNotEqual(again.returncode,0)
        self.assertEqual((output/'reconstruction-report.json').read_bytes(),receipt)

    def test_thin_component_fails_before_baking(self):
        output=self.folder/'thin-output';result=self.invoke(SCRIPT,self.arguments('thin.blend',output))
        self.assertNotEqual(result.returncode,0)
        report=json.loads((output/'reconstruction-report.json').read_text())
        self.assertEqual(report['status'],'failed');self.assertIn('THIN_COMPONENT',report['error'])
        self.assertFalse((output/'candidate.blend').exists())

if __name__=='__main__':unittest.main()
