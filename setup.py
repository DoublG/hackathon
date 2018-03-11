from setuptools import setup, find_packages

setup(
    name='Hackathon',
    version='0.0.1',
    description='Hackathon test scripts',
    author='Erik Woidt',
    packages=find_packages(exclude=['tests', 'venv']),
    package_data={
        'hackathon': ['data/recommendation/*.csv','data/trip_examples/*.gpx'],
    },
    entry_points={
        'console_scripts': [
            'display_graph=hackathon.__init__:display_graph',
            'find_intersects=hackathon.__init__:find_intersectionpoints',
            'similar_routes=hackathon.__init__:similar_routes',
            'calculate_initial_rating=hackathon.ratings.__init__:calculate_initial_rating',
            'update_rating=hackathon.ratings.__init__:update_rating'
        ],
    },
    install_requires=['matplotlib==2.1.2', 'networkx==2.1', 'pyspark==2.3.0','scipy==1.0.0'],
)
