from setuptools import setup, find_packages

setup(name='pyrrha-pynode',
      description='Python version of pandora worker node, for Pyrrha version of Pandora Boxchain',
      long_description="""
            Pandora worker node - is server application that allows    
            rovide server capacity for calculations.
            Calculations are conducted in the field of Deep learning     
            (training operation or prediction)
      """,
      version='0.1.3',
      author="""
              Dr Maxim Orlovsky <orlovsky@pandora.foundation>,
              Sergey Korostelyov <striderbox@gmail.com>'
              """,
      install_requires=[],
      packages=find_packages(),
      license='MIT'
      )
