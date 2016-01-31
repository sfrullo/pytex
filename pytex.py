import json
import argparse
import os
import os.path as path

sec_lev =  ['\section', '\subsection', '\subsubsection', '\paragraph']

def make_directory(root, section, level):
    if isinstance(section, str):
        try:
            print('Make dir: ' + path.join(root, section))
            os.makedirs(path.join(root, section))
            os.makedirs(path.join(root, section, 'fig'))
        except OSError:
            pass
        f = open(path.join(root, section, section + '.tex'), 'w+')
        f.write(sec_lev[level] + '{' + section + '}\n')
        f.close()
    elif isinstance(section, dict):
        for k,v in section.items():
            if not v:
                make_directory(root, k, level)
            else:
                make_directory(path.join(root, k), v, level+1)

    elif isinstance(section, list):
        for s in section:
            make_directory(root, s, level)

def make_tex_file(root_dir, data):

    documentclass = data["documentclass"]
    documentinfo = data["documentinfo"]
    packages = data["packages"]
    sections = data["sections"]
    bibtex = data["bibtex"]

    with open(path.join(root_dir, 'main.tex'), 'w') as f:
        f.write('\documentclass')
        if hasattr(documentclass, 'option'):
            f.write('[')
            f.write(', '.join(documentclass['option'].values()))
            f.write(']')
        f.write('{' + documentclass['class'] + '}\n')


        for k, v in packages.items():
            if k == 'use':
                for name, opt in v.items():
                    f.write('\\usepackage')
                    if isinstance(opt,str):
                        f.write('[' + opt + ']')
                    f.write('{' + name + '}\n')
            else:
                f.write('\\' + k + '{')
                for name,val in v.items():
                    if val:
                        if isinstance(val,str):
                            val = '{' + val + '}'
                        if isinstance(val,list):
                            val = '{' + ', '.join(str(val)) + '}'
                        f.write('\t' + name + '=' + val + '\n')
                    else:
                        f.write(k + ',')
                f.write('}')


        for k,v in documentinfo.items():
            if isinstance(v,str):
                f.write('\\' + k + '{' + v + '}\n')
            else:
                [f.write('\\' + k + '{' + val + '}\n') for val in v.values() ]

        f.write('\\begin{document}\n')
        for root, dirnames, files in os.walk(root_dir):
            print(root, dirnames, files)
            for filename in files:
                print(filename)
                if '.tex' in filename:
                    f.write('\\include{' + path.join(root, dirnames, filename) + '}\n')
        
        if bibtex:
            f.write('\\bibliographystyle{' + bibtex['style'] + '}\n')
            f.write('\\bibliography{' + bibtex['location'] + '}\n')                        
        f.write('\\end{document}\n')  


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Pytex makes directory tree and basic files for latex projects")
    parser.add_argument('-i', dest='inputfile', help='input files')
    parser.add_argument('--yaml', action='store_const', const=True, dest='is_yaml', help='Flag to use yaml file')
    parser.add_argument('--pdir', dest='project_dir', help='Project\'s root directory')   
    args = parser.parse_args()
    print(args)

    # Parse JSON/YAML file
    data = ''.join(open(args.inputfile, 'r').readlines())
    data = json.loads(data)

    # Make directory tree
    sections = data["sections"]
    root_dir = path.abspath(args.project_dir)
    make_directory(root_dir, sections, 0)
    
    # Make main Tex file
    make_tex_file(root_dir, data)