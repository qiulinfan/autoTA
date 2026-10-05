import importlib.util
from pathlib import Path
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'skills/auto-ta/scripts/blender_reconstruct.py'
spec=importlib.util.spec_from_file_location('reconstruct',SCRIPT)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class ReconstructionPolicyTests(unittest.TestCase):
    def test_budget_tolerance(self):
        self.assertEqual(module.polygon_range(2000),(1600,2400))
        self.assertEqual(module.polygon_range(500),(400,600))
        with self.assertRaises(ValueError):module.polygon_range(1000,.21)

    def test_allocations_retain_small_meshes(self):
        result=module.allocate_budget([100,1,1],2000)
        self.assertEqual(sum(result),2000)
        self.assertTrue(all(x>=24 for x in result))
        self.assertGreater(result[0],result[1])

    def test_impossible_budget_fails(self):
        with self.assertRaises(ValueError):module.allocate_budget([1,1],40)
        with self.assertRaises(ValueError):module.allocate_budget([0,1],1000)

if __name__=='__main__':unittest.main()
