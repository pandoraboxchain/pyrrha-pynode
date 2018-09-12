from setuptools import setup

setup(name='core',
      version='0.1.3',
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
