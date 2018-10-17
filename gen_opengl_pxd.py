import argparse
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
    if node.attrib['name'] == 'GLhandleARB':
      outf.write('  ctypedef int ' + node.attrib['name'] + '\n')
      return

    print('Skipping: ' + node.tag + ' ' + str(node.attrib))
    return

  text = ''.join(node.itertext())

  if 'api' in node.attrib and node.attrib['api'] != 'gl':
    print('Skipping: ' + text)
    return

  text = (text
    .replace('khronos_intptr_t', 'int *')
    .replace('khronos_ssize_t', 'int')
    .replace('khronos_float_t', 'float')
    .replace('khronos_int8_t', 'int')
    .replace('khronos_uint8_t', 'int')
    .replace('khronos_int16_t', 'int')
    .replace('khronos_uint16_t', 'int')
    .replace('khronos_int32_t', 'int')
    .replace('khronos_uint32_t', 'int')
    .replace('khronos_int64_t', 'int')
    .replace('khronos_uint64_t', 'int')
    .replace('uint64_t', 'int')
    .replace('int64_t', 'int')
    .replace('struct __GLsync *', 'int *')
    .replace('(void)', '()'))

  if text.startswith('struct'):
    print('Skipping: ' + text)
    return

  if text.startswith('typedef'):
    outf.write('  c' + text[:-1] + '\n')
    return

  raise NotImplementedError(text)


def gen_types(outf, node):
  assert node.tag == 'types'
  for child in node:
    gen_type(outf, child)
  outf.write('\n')


def gen_enum(outf, node):
  assert node.tag == 'enum'
  if 'api' in node.attrib and node.attrib['api'] != 'gl':
    print('Skipping: ' + node.attrib['name'])
    return
  outf.write('  GLenum ' + node.attrib['name'] + '\n')


def gen_group(outf, node):
  assert node.tag == 'group'
  for child in node:
    gen_enum(outf, child)


def gen_groups(outf, node):
  assert node.tag == 'groups'
  # for child in node:
  #   gen_group(outf, child)


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
      param_name = child.find('name')
      if param_name.text == 'in':
        param_name.text += '_'
      params.append(''.join(child.itertext()))
  
  decl += '(' + ', '.join(params) + ')'

  if 'struct _cl_context *' in decl:
    print('Skipping: ' + decl)
    return

  outf.write('  ' + decl + '\n')


def gen_commands(outf, node):
  assert node.tag == 'commands'
  outf.write('\n')
  for child in node:
    gen_command(outf, child)


def gen_pxd(outf, root, incl):
  gen_license_info(outf, root[0])

  outf.write('cdef extern from ' + incl + ':\n')

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
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument('--include', '-i', type=str, default='<gl.h>')
  arg_parser.add_argument('--output', '-o', type=str, default='opengl.pxd')
  args = arg_parser.parse_args()

  incl = args.include
  if len(incl) == 0 or incl[0] not in ['\'', '"']:
    incl = '"' + incl + '"'

  root = xml.etree.ElementTree.parse('extern/OpenGL-Registry/xml/gl.xml').getroot()
  with open(args.output, 'w') as outf:
    gen_pxd(outf, root, incl)
