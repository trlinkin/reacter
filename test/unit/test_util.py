#!/usr/bin/env python
import unittest
from reacter.util import Util

class UnitTestUtil(unittest.TestCase):

  def test_parse_destination(self):
  # test given host, default port
    self.assertEqual(Util.parse_destination('localhost'), ['localhost', Util.DEFAULT_PORT])
  # test given host and port
    self.assertEqual(Util.parse_destination('localhost:1234'), ['localhost', 1234])

  
  def test_parse_agents(self):
  # test empty input string
    self.assertEqual(Util.parse_agents(''), [])
  # test single item
    self.assertEqual(Util.parse_agents('test'), ['test'])
  # test comma-separated list
    self.assertEqual(Util.parse_agents('test1,test2'), ['test1', 'test2'])


  def test_dict_get(self):
    test = {
      'options': {
        'unthinkable1': True,
        'unthinkable2': False,
        'unthinkable3': 'yes',
        'unthinkable5': 1,
      },

      'values': [1,2,3,4]
    }

  # test existing values
    self.assertEqual(Util.dict_get(test, 'options.unthinkable1'), True)
    self.assertEqual(Util.dict_get(test, 'options.unthinkable2'), False)
    self.assertEqual(Util.dict_get(test, 'options.unthinkable3'), 'yes')
    self.assertEqual(Util.dict_get(test, 'options.unthinkable5'), 1)
    self.assertEqual(Util.dict_get(test, 'values'), [1,2,3,4])

  # test fallbacks
    self.assertIsNone(Util.dict_get(test, 'options.unthinkable4'))
    self.assertEqual(Util.dict_get(test, 'options.unthinkable4', 'fallback'), 'fallback')
    self.assertEqual(Util.dict_get(test, 'thegame', []), [])


  def test_camelize(self):
  # test basics
    self.assertEqual(Util.camelize('hello'), 'Hello')
    self.assertEqual(Util.camelize('yes'), 'Yes')
    self.assertEqual(Util.camelize('this_is_dog'), 'ThisIsDog')

  # test prefix/suffix
    self.assertEqual(Util.camelize('yes_this_is_dog', 'Hello, '), 'Hello, YesThisIsDog')
    self.assertEqual(Util.camelize('hello_yes', suffix=' This is Dog'), 'HelloYes This is Dog')
    self.assertEqual(Util.camelize('yEs_tHiS', 'hElLo', ' iS DoG'), 'hElLoYesThis iS DoG')


if __name__ == '__main__':
    unittest.main()
