#!/usr/bin/env python3
"""Show modules presence in nginx packages side-by-side in a grid."""
import subprocess
from collections import OrderedDict


def main():
    """Main Function."""
    packages_all = (
        'nginx-extras',
        'nginx-full',
        'nginx-core',
        'nginx-light'
    )

    modules = OrderedDict()
    max_module_len = 0

    for index, package in enumerate(packages_all):
        print('Gathering package descriptions... {index}/{all}'.format(
            index=index+1, all=len(packages_all)))
        package_description = get_package_description(package)

        # generate module lists
        description_parts = package_description.split(".")
        modules_grouped = [
            part.split(': ')
            for part in description_parts
            if 'MODULES' in part
        ]

        for group in modules_grouped:
            group_name = group[0].strip()

            group_module_list = group[1].replace('\n', '')
            group_module_list = group_module_list.split(", ")

            for module in group_module_list:
                # modules need to be unique across groups
                # plus, this will make sorting easy
                module_id = '{group}__{module}'.format(
                    group=group_name.upper(), module=module.lower())

                if module_id in modules:
                    modules[module_id].append(package)
                else:
                    modules.update({module_id : [package]})

                # save max. module length
                if len(module) > max_module_len:
                    max_module_len = len(module)


    # sort by key
    modules_sorted = OrderedDict(sorted(modules.items(), key=lambda t: t[0]))
    # more natural sorting, but corrupt grouping:
    # modules_sorted = modules

    print_grid(modules_sorted, max_module_len, packages_all)



def get_package_description(package):
    """Get the package information from apt-cache and return the
    description part.
    If multiple package versions are present, focus on the last one.
    """
    try:
        apt_output = subprocess.check_output(
            ['apt-cache', 'show', package],
            universal_newlines=True)
    except subprocess.CalledProcessError:
        print('Error: "apt-cache" was not able to retrieve package info.')
        exit(1)
    except FileNotFoundError:
        print('Error: "apt-cache" could not be found on your machine.\n'
              'Install it on Debian-like distributions via:\n'
              '  sudo apt-get install apt')
        exit(1)
    finally:
        pass

    # if multiple packages found, use only last occurence
    seperator = 'Package: {package_name}'.format(package_name=package)
    last_package = apt_output.rpartition(seperator)[2]
    # return Description part
    return last_package.partition('Description')[2]



def print_grid(modules_sorted, max_module_len, packages_all):
    """Print the data in a grid view.
    The first row will contain the package names,
    from the second onwards all modules either display Y or N
    depending on their occurence in that package.
    """
    print(''.ljust(max_module_len), end='|')
    for package in packages_all:
        heading = '{:^14}'.format(package)
        print(heading, end='|')
    print()

    previous_group = ''
    for module_id, packages in modules_sorted.items():
        group, module = module_id.split('__')

        # print group_name if changed
        if group != previous_group:
            print(group)
            previous_group = group

        print(module.ljust(max_module_len), end='|')

        for package in packages_all:
            if package in packages:
                print('{:^14}'.format('Y'), end='|')
            else:
                print('{:^14}'.format('N'), end='|')
        print('')


if __name__ == '__main__':
    main()
