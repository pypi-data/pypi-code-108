import click
import os
import shutil
import inspect


# validation on project name - return bad_parameter_error if project_name contains space
def project_name_validation(ctx, param, value):
    try:
        project_name = value
        if ' ' not in project_name:
            return project_name
        else:
            raise click.BadParameter(
                'The project_name need to be without spaces')
    except ValueError:
        click.echo('Incorrect project_name: {}'.format(project_name))
        value = click.prompt(param.prompt)
        return project_name_validation(ctx, param, value)


@click.command()
# ask for root to folder
@click.option('--root', '-r',  help='Specify root of project''s folder', default='.', prompt="folder root")
# ask for Project name
@click.option('--project_name', '-n', prompt="Project_name",
              help='Specify a project name without spaces', callback=project_name_validation)
# ask for root to api_id
@click.option('--api_id', '-id',  prompt=True, help='The user API_ID. '
                                                    'See badook''s web application-->Settings for further info')
# ask for root to api_key
@click.option('--api_key', prompt=True, hide_input=True, help='The user API_Key for authentication'
                                                              'See badook''s web application-->Settings for further info')
@click.option('--base_uri', '-u',
              help='Specify uri for runtime badook. defult set to https://runtime.badook.ai/services/',
              default='https://runtime.badook.ai/services/')
def Process(project_name, root, api_id, api_key, base_uri):
    click.echo('Project set to {}'.format(project_name))
    # Define folders path by root + project name
    path = f"{root}/{project_name}"
    if not os.path.exists(path):
        """Create folders according to root tree:
        root
        | -> tests /
        | | -> test_example.py
        | ->.badook /
        | | -> config / default.yaml
        | ->.gitignore
        """
        folders = {"/tests", "/.badook", "/.gitignore"}
        for folder in folders:
            os.makedirs(path+folder)
        # create test_example.py with
        with open(path+'/tests/test_example.py', 'w') as f:
            # Summary and tests code exmaples
            text = """
            #This file containes stractures of summaries, tests and assertions built with badook-ai

            from badook_tests.test import TestCase
            class RealEstateTestCase(TestCase):
            def set_up(self):
            # setup dataset and feature level summaries
            def test_feature_distribution(self):

            # Summaries
            def set_up(self):
            context = BadookContext(client_id="", client_secret="")

            ## Defining a dataset level summary
            self.real_estate_summary = context \
            .from_dataset('realestateData') \
            .set_name('real_estate_summary')

            ## Defining a feature level numeric summary
            type_sub = NumericSummary(feature='price', name='sub_price') \
            .group_by('type', 'suburb')
            .on(Self.real_estate_summary)

            self.summary_builder.add_summary(type_sub)


            #Test containing dataset level checks:
            def test_real_estate_summary_dataset(self):
            self.real_estate_summary.features.check(f => 'price'))
            self.real_estate_summary.records.compare_to(ComparisonPoint.LAST)
            .check(current, past => current.count >= past.count)
            """
            f.write(text)

        # Ask for the user an api_key and user_id and create .yaml file
        os.mkdir(path+'/.badook/config')
        text = inspect.cleandoc("""base_uri: '"""+base_uri+"""'
            api_key:'""" + api_id + """'
            secret_key:'""" + api_key + """'
            project_name:'"""+project_name+"""'
            """)
        # save configuration to .yaml file. 3 last row are indent
        with open(path+'/.badook/config/default.yaml', 'w') as f:
            f.write(text)

        # Create .goignore file in path/gitignore with instruction to ignore the .badook folder
        text_ignore = inspect.cleandoc("""#ignore all files in path/.badook/ folder
                        .badook""")

        with open(path+'/.gitignore/.gitignore', 'w') as f:
            f.write(text_ignore)

        click.echo(f"\nDirectory was created at {path}")

    else:
        # delete the folder structure everytime running this command - for tests only
        # shutil.rmtree(path,ignore_errors=True)
        click.echo(f"\n Directory {project_name} is already exists")


if __name__ == '__main__':
    Process(None, None, None, None, None)
