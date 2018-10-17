import sys
import xml.etree.ElementTree


def gen_license_info(outf, node):
  assert node.tag == 'comment'
  license_info = ('''\

 This file was derived from gl.xml in the OpenGL API registry. The license
 in that file is reproduced below:

''')
  license_info += '\n'.join('# ' + line for line in node.text.split('\n'))
  license_info = '\n'.join('#' + line for line in license_info.split('\n'))

  outf.write(license_info + '\n\n')


def gen_type(outf, node):
  assert node.tag == 'type'
  if len(node) == 0:
    print('Skipping: ' + node.tag + ' ' + str(node.attrib))
    return

  text = ''.join(node.itertext())

  if text.startswith('typedef'):
    outf.write('  c' + text[:-1] + '\n')
    return

  if text.startswith('struct') and '{' not in text:
    return

  raise NotImplementedError(text)


def gen_types(outf, node):
  assert node.tag == 'types'
  for child in node:
    gen_type(outf, child)
  outf.write('\n')


def gen_enum(outf, node):
  assert node.tag == 'enum'
  outf.write('  GLenum ' + node.attrib['name'] + '\n')


def gen_group(outf, node):
  assert node.tag == 'group'
  for child in node:
    gen_enum(outf, child)


def gen_groups(outf, node):
  assert node.tag == 'groups'
  for child in node:
    gen_group(outf, child)


def gen_enums(outf, node):
  assert node.tag == 'enums'
  for child in node:
    if child.tag == 'unused': continue
    gen_enum(outf, child)


def gen_command(outf, node):
  assert node.tag == 'command'
  decl = ''.join(node.find('proto').itertext())

  params = []
  for child in node:
    if child.tag == 'param':
      params.append(''.join(child.itertext()))
  
  decl += '(' + ', '.join(params) + ')'
  outf.write('  ' + decl + '\n')


def gen_commands(outf, node):
  assert node.tag == 'commands'
  outf.write('\n')
  for child in node:
    gen_command(outf, child)


def gen_pxd(outf, root):
  gen_license_info(outf, root[0])

  outf.write('cdef extern from <TODO.h>:\n')

  for child in root[1:]:
    if child.tag == 'types':
      gen_types(outf, child)
    elif child.tag == 'groups':
      gen_groups(outf, child)
    elif child.tag == 'enums':
      gen_enums(outf, child)
    elif child.tag == 'commands':
      gen_commands(outf, child)
    elif child.tag == 'feature':
      pass
    elif child.tag == 'extensions':
      pass
    else:
      raise NotImplementedError(child.tag, child.attrib)


if __name__ == '__main__':
  root = xml.etree.ElementTree.parse('extern/OpenGL-Registry/xml/gl.xml').getroot()
  with open('opengl.pxd', 'w') as outf:
    gen_pxd(outf, root)
