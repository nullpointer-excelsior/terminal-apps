import os
import click

def get_file_type(file_name):
    return os.path.splitext(file_name)[1][1:] or 'txt'

def read_directory(directory, ignore_ext=None, ignore_dirs=None):
    ignore_ext = ignore_ext or []
    ignore_dirs = ignore_dirs or []
    ignore_dirs.append('node_modules')
    ignore_dirs.append('venv')

    files_summary = []
    files_details = []

    for root, _, files in os.walk(directory):
        # Ignorar directorios especificados
        if any(ignored_dir in root for ignored_dir in ignore_dirs):
            continue

        for file in files:
            file_ext = get_file_type(file)

            # Ignorar extensiones especificadas
            if file_ext in ignore_ext:
                continue

            file_path = os.path.join(root, file)
            files_summary.append(f"- {file_path}")
            with open(file_path, 'r') as f:
                content = f.read()
            files_details.append(f"**{file_path}**\n\n```{file_ext}\n{content}\n```")

    return files_summary, files_details

def create_markdown_summary(title, directory, output_file, ignore_ext, ignore_dirs):
    files_summary, files_details = read_directory(directory, ignore_ext, ignore_dirs)

    with open(output_file, 'w') as md_file:
        md_file.write(f"# {title}\n\n")
        md_file.write("## Lista de archivos\n")
        md_file.write("\n".join(files_summary))
        md_file.write("\n\n## Archivos\n")
        md_file.write("\n\n".join(files_details))


@click.command(help='Muestra los archivos y el codigo de un directorio en formato markdown')
@click.option('-t','--title', required=True, help="Title of the scan")
@click.option('-d','--directory', required=True, help="Directory to scan")
@click.option('-o','--output', default='summary.md', help="Output file name and path")
@click.option('-ix','--ignore-ext', help="Comma-separated list of file extensions to ignore (e.g., py,txt)")
@click.option('-id','--ignore-directory', help="Comma-separated list of directories to ignore")
def proyect_scanner(title, directory, output, ignore_ext, ignore_directory):
    ignore_ext_list = ignore_ext.split(",") if ignore_ext else []
    ignore_dirs_list = ignore_directory.split(",") if ignore_directory else []

    create_markdown_summary(title, directory, output, ignore_ext_list, ignore_dirs_list)
