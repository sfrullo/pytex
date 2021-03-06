import json
import argparse
import os
import os.path as path

sec_lev = ['\section', '\subsection', '\subsubsection', '\paragraph']
lab_lev = ['sec:', 'subsec:', 'subsubsec:', 'par:']

def make_directory(root, section, level):
    if isinstance(section, str):
        try:
            print('Make dir: ' + path.join(root, section))
            os.makedirs(path.join(root, section.replace(' ', '-')))
            os.makedirs(path.join(root, section.replace(' ', '-'), 'fig'))
        except OSError:
            pass
        f = open(path.join(root, section.replace(' ', '-'), section.replace(' ', '-') + '.tex'), 'w')
        f.write(sec_lev[level] + '{' + section + '}\n')
        f.write('\\label{' + lab_lev[level] + section +'}\n')
        f.close()
    elif isinstance(section, dict):
        for k,v in section.items():
            try:
                os.makedirs(path.join(root, k.replace(' ', '-')))
            except OSError:
                pass
            f = open(path.join(root, k.replace(' ', '-'), k.replace(' ', '-') + '.tex'), 'w')
            f.write(sec_lev[level] + '{' + k + '}\n')
            f.write('\\label{' + lab_lev[level] + k +'}\n')
            f.close()
            make_directory(path.join(root, k), v, level+1)
    elif isinstance(section, list):
        for s in section:
            make_directory(root, s, level)

def get_tex_files(root, section):
    files = list()
    if isinstance(section, str):
        return [path.join(root, section.replace(' ', '-'), section.replace(' ', '-') + '.tex')]
    elif isinstance(section, list):
        for s in section:
            files += get_tex_files(root,s)
        return files
    elif isinstance(section,dict):
        for k,v in section.items():
            files += [path.join(root, k.replace(' ', '-'), k.replace(' ', '-') + '.tex')]
            files += get_tex_files(path.join(root, k),v)
        return files

def make_tex_file(root_dir, data):

    documentclass = data["documentclass"]
    documentinfo = data["documentinfo"]
    packages = data["packages"]['use']
    pkg_setup = data["packages"]['setup']
    sections = data["sections"]
    bibtex = data["bibtex"]

    with open(path.join(root_dir, 'main.tex'), 'w') as f:
        f.write('\documentclass')
        if documentclass['option']:
            f.write('[')
            f.write(', '.join(documentclass['option']))
            f.write(']')
        f.write('{' + documentclass['class'] + '}\n')
        f.write('\n')

        for name, opt in packages.items():
            f.write('\\usepackage')
            if isinstance(opt,str):
                f.write('[' + opt + ']')
            f.write('{' + name + '}\n')
        
        for k,v in pkg_setup.items():
            f.write('\\' + k + '{\n')
            opt = list()
            for name,val in v.items():
                if not val == None:
                    if isinstance(val, str):
                        opt += ['\t' + name + '={' + val + '}']
                    if isinstance(val,list):
                        opt += ['\t' + name + '={' + ', '.join(map(str,val)) + '}']
                    if val == 'false':
                        opt += ['\t' + name + '=false']
                    if val == 'true':
                        opt += ['\t' + name + '=true']
                else:
                    opt += ['\t' + name]
            f.write(',\n'.join(opt))
            f.write('}\n')
        f.write('\n')


        for k,v in documentinfo.items():
            if isinstance(v,str):
                f.write('\\' + k + '{' + v + '}\n')
            else:
                [f.write('\\' + k + '{' + val + '}\n') for val in v ]
            f.write('\n')


        f.write('\\begin{document}\n\n')
        f.write('\t\\maketitle\n\n')
        f.write('\t\\begin{abstract}\n\n\t\\end{abstract}\n\n')
        #for root, dirnames, files in os.walk(root_dir):
        #    for filename in files:
        #        if not filename == 'main.tex' and filename.endswith('.tex'):
        #            f.write('\\include{' + path.join(root,filename) + '}\n\n')
        
        for s in get_tex_files(root_dir, sections):
            f.write('\t\\input{' + path.relpath(s, root_dir) + '}\n\n')


        if bibtex:
            f.write('\t\\bibliographystyle{' + bibtex['style'] + '}\n')
            if bibtex['location']:
                f.write('\t\\bibliography{' + bibtex['location'] + '}\n')
            else:
                try:
                    os.makedirs(path.join(root_dir, 'bib'))
                except OSError:
                    pass
                open(path.join(root_dir, 'bib', 'bibliography.bib'), 'w').close()
                f.write('\t\\bibliography{' + path.join(root_dir, 'bib', 'bibliography.bib') + '}\n')
        
        f.write('\n')
        f.write('\\end{document}\n')  


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Pytex makes directory tree and basic files for latex projects")
    parser.add_argument('-i', dest='inputfile', help='input files')
    parser.add_argument('--yaml', action='store_const', const=True, dest='is_yaml', help='Flag to use yaml file')
    parser.add_argument('--pdir', dest='project_dir', help='Project\'s root directory')   
    args = parser.parse_args()
    #print(args)

    # Parse JSON/YAML file
    print('Import: ' + args.inputfile + '...', end='')
    data = ''.join(open(args.inputfile, 'r').readlines())
    data = json.loads(data)
    print('done')

    # Make directory tree
    print('Make directories at ' + path.abspath(args.project_dir) + '...')
    sections = data["sections"]
    root_dir = path.abspath(args.project_dir)
    make_directory(root_dir, sections, 0)
    print('done')    

    # Make main Tex file
    print('Create main.tex ...', end='');
    make_tex_file(args.project_dir, data)
    print('done')