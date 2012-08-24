#!/usr/bin/env python

import unittest
import subprocess
import shutil
import os
import yaml


class IntTestReacter(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.dir = './__tests'

    try:
      shutil.rmtree(cls.dir)
    except:
      pass

    os.mkdir(cls.dir)
    os.chdir(cls.dir)

  @classmethod
  def tearDownClass(cls):
    os.chdir('..')
    shutil.rmtree(cls.dir)

  def given_config(self, config={}):
    with open(os.path.join('reacter.yaml'), 'w') as f:
      f.write(yaml.dump(config))

  def run_reacter(self, *args):
    p = subprocess.Popen(['../../../../bin/reacter'] + ['-H', 'amq', '-R', '-c', 'reacter.yaml'] + list(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, _ = p.communicate()
    self.reacter_output = stdout

  def test_exec_basic(self):
    self.given_config({
    'reacter': {
       'options': {
         'queue': {
            'host': 'amq'
          }
        }
      }
    })

    print 'Go'

    self.run_reacter()

    print self.reacter_output


if __name__ == '__main__':
    unittest.main()