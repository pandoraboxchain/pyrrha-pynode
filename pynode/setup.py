from distutils.core import setup
from setuptools import setup, find_packages

setup(name='core',
      version='0.1.0-alpha',
      author="""
              Dr Maxim Orlovsky <orlovsky@pandora.foundation>,
              Sergey Korostelyov <striderbox@gmail.com>'
              """,
      install_requires=[],
      packages=['core',
                'core.job',
                'core.node',
                'core.patterns',
                'core.processor',
                'core.processor.entities'],
      license='MIT'
      )
