# encoding=utf-8

import warnings

from hansken.query import Facet, Term
from hansken.remote import ProjectContext
from hansken.tool import add_command


def run_stats_command(args):
    """
    Performs some sanity checks and runs `.stats` with arguments from ``args``.

    :param args: an `argparse.Namespace` object with parsed arguments
    :return: 0
    """
    if not args.endpoint:
        stats_parser.error('the following argument is required: ENDPOINT')
    if not args.project:
        stats_parser.error('the following argument is required: PROJECT')

    stats(args.endpoint, args.project, args.images,
          show_image_props=args.show_image_props, show_type_counters=args.show_type_counters,
          auth=args.auth, verify=args.verify)
    return 0


def run_stats(*args, **kwargs):
    warnings.warn('{0}.run_stats has been renamed to {0}.run_stats_command'.format(__name__),
                  DeprecationWarning)
    run_stats_command(*args, **kwargs)


def stats(base_url, project, images=None, show_image_props=False, show_type_counters=True, auth=None,
          verify=True):
    """
    Generate per-image statistics for a project. Prints meta-data of each
    image in a project, followed by type counters for traces within that image.
    Prints output in multi-document YAML syntax.

    :param base_url: HTTP endpoint to a Hansken gatekeeper (e.g.
        https://hansken.nl/gatekeeper)
    :param project: project id to generate stats for
    :param images: image ids to generate stats for (or all images when falsy)
    :param show_image_props: show all image properties, not just id and name
    :param show_type_counters: show trace type counters per image
    :param auth: `HanskenAuthBase <hansken.auth.HanskenAuthBase>` instance to
        handle authentication, or `None`
    """
    with ProjectContext(base_url, project, auth=auth, verify=verify) as context:
        # predefine a type facet
        facet = Facet('type', size=1024)

        project_images = context.images()
        if images:
            # if images were specified, filter the project images here
            images = [image for image in project_images if image.get('id') in images]
        else:
            # otherwise process all images
            images = project_images

        for image in images:
            # TODO: use image.state shorthand on a future Image object (HANSKENPY-10)
            # states is messy, take just the last state if available and format it
            if len(image.get('states', [])):
                image['state'] = image.pop('states')[-1]
                image['state'] = '{state} ({date})'.format(**image['state'])

            # execute query within the project, we don't want traces, just the total and the facet
            results = context.search(query=Term('image', image.get('id')),
                                     count=0,
                                     facets=facet)
            types = results.facets[0]

            try:
                print('---')  # YAML document start
                # print id and name (default 'null' to avoid None)
                print('{name:<20} {value}'.format(name='id:', value=image.pop('id', 'null')))
                print('{name:<20} {value}'.format(name='description:', value=image.pop('description', 'null')))

                if show_image_props:
                    # print remaining image properties, sorted by name
                    for name, value in sorted(image.items()):
                        print('{name:<20} {value}'.format(name=name + ':', value=value))

                # include the total number of traces
                print('{name:<20} {value}'.format(name='traces:', value=len(results)))

                if types and show_type_counters:
                    # print type counters (already ordered by decreasing count)
                    print('types:')
                    for counter in types.values():
                        print('  {label:<18} {count}'.format(label=counter.label + ':', count=counter.count))
            finally:
                print('...')  # YAML document end


# define command stats
stats_parser = add_command('stats',
                           run_stats_command,
                           optional_project=False,
                           help='generate statistical information for each image linked to a project')
stats_parser.add_argument('project', metavar='PROJECT',
                          help='generate stats for PROJECT')
stats_parser.add_argument('images', metavar='IMAGE', nargs='*',
                          help='only generate stats for IMAGE within PROJECT '
                               '(defaults to all images)')
stats_parser.add_argument('--image-properties', '-i', dest='show_image_props', action='store_true', default=False,
                          help='show all image properties')
stats_parser.add_argument('--no-image-properties', '-I', dest='show_image_props', action='store_false',
                          help="don't show all image properties (just id and description, this is the default)")
stats_parser.add_argument('--type-counters', '-c', dest='show_type_counters', action='store_true', default=True,
                          help='show type counters for each image (this is the default)')
stats_parser.add_argument('--no-type-counters', '-C', dest='show_type_counters', action='store_false',
                          help="don't show type counters for each image")
