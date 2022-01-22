from setuptools import setup
long_description = "data_checker1453 is a package used to preview details of the dataframes in the first steps of data exploration. <br> \n It has more specific functionality for displaying texts side by side as well as dataframes. <br> \n Usage: <br> \n Mehods and functions : <br> \n\n show_preview() : A method to check basic details about the dataframe in question. To use this method instantiate the Check() class with your dataframe as an argument, then call show_preview()<br> \n\n display_side_by_side : A function to display 2 dataframes side by side (make sure you limit the column numbers so it would fit the screen) <br> \n\n print_side_by_side :  A function to print 2 or 4 strings side by side (make sure you don't exceed the charachter size & for 4 strings pass b = 2) <br>"
setup(name='data_checker1453',
      version='0.35',
      description='package to offer basic previews to the data',
      packages=['data_checker1453'],
      author = 'Mohamad AlZainy',
      author_email = 'zainy1453@gmail.com',
      long_description=long_description,
      long_description_content_type="text/markdown", 
      zip_safe=False)
