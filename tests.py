import unittest
import algorithm_factory as af

class testAlgFactory(unittest.TestCase):
	def test_traffic(self):
		trafficalg = af.factory("traffic")
		print(trafficalg.description)

if __name__ == "__main__":
	unittest.main()
