import setuptools
import os

class InstallCommand(setuptools.command.install.install):
    def run(self):
        # CREATE UNTRACKED DIRECTORIES
        untracked_directories = [os.path.join('filesystem', 'public', 'viewable')]  # List your directories here
        for directory in dirs_to_create:
            if not os.path.exists(directory):
                os.makedirs(directory)
        super().run()

setuptools.setup(name = 'MailSPHINX',
                 version = '1.0.0',
                 author = 'Luke Stegeman on behalf of the SPHINX Collaboration',
                 author_email = 'luke.a.stegeman@nasa.gov',
                 description = 'Sends validation report emails to subscribers at a regular cadence.',
                 long_description = open('README.md').read(),
                 long_description_content_type = 'text/markdown',
                 url = 'https://github.com/lukestegeman/mailsphinx',
                 packages = setuptools.find_packages(),
                 classifiers = [
                                'Programming Language :: Python :: 3',
                                'License :: OSI Approved :: MIT License',
                                'Operating System :: OS Independent',
                               ],
                 python_requires = '>=3.10.5',
                 install_requires = [],
                 cmdclass = {
                             'install': InstallCommand,
                            },
                )
