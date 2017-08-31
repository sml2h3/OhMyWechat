#!/usr/bin/python3  
# -*- coding: utf-8 -*-
# ----------------------------
# |   Author:sml2h3          |
# |   Email:sml2h3@gmail.com |
# ----------------------------

"""Thunder Chen<nkchenz@gmail.com> 2007.9.1"""

from __future__ import with_statement
import re

try:
    import xml.etree.ElementTree as ET
except:  # pragma: no cover
    # For older versions of Python.
    import cElementTree as ET

from System.Wechat.Login.object_dict import object_dict


class XML2Dict(object):
    """Turn XML into a dictionary data structure."""

    def _parse_node(self, node):
        node_tree = object_dict()
        if node.text and node.attrib:
            if node.tag in node.attrib:
                raise ValueError("Name conflict: Attribute name conflicts with "
                                 "tag name. Check the documentation.")
            node.attrib.update({node.tag: node.text})
            node.text = ''
        # Save attrs and text. Fair warning, if there's a child node with
        # the same name as an attribute, values will become a list.
        if node.text and node.text.strip():
            node_tree = node.text
        else:
            for k, v in node.attrib.items():
                k, v = self._namespace_split(k, v)
                node_tree[k] = v
            # Save children.
            for child in node.getchildren():
                tag, tree = self._namespace_split(child.tag, self._parse_node(child))
                if tag not in node_tree:  # First encounter, store it in dict.
                    node_tree[tag] = tree
                    continue
                old = node_tree[tag]
                if not isinstance(old, list):
                    # Multiple encounters, change dict to a list
                    node_tree.pop(tag)
                    node_tree[tag] = [old]
                node_tree[tag].append(tree)  # Add the new one.
        return node_tree

    def _namespace_split(self, tag, value):
        """
           Split the tag  '{http://cs.sfsu.edu/csc867/myscheduler}patients'
             ns = http://cs.sfsu.edu/csc867/myscheduler
             name = patients
        """
        result = re.compile("\{(.*)\}(.*)").search(tag)
        if result:
            tag = result.groups(1)
            # value.namespace, tag = result.groups()
        return (tag, value)

    def parse(self, file):
        """Parse an XML file to a dict."""
        with open(file, 'r') as f:
            return self.fromstring(f.read())

    def fromstring(self, s):
        """Parse an XML string into a dict."""
        t = ET.fromstring(s)
        root_tag, root_tree = self._namespace_split(t.tag, self._parse_node(t))
        return object_dict({root_tag: root_tree})


class Dict2XML(object):
    """Turn a dictionary into an XML string."""

    def tostring(self, d):
        """Convert dictionary to an XML string."""
        if not isinstance(d, dict):
            raise TypeError('tostring must receive a dictionary: %r' % d)
        if len(d) != 1:
            raise ValueError('Dictionary must have exactly one root element')
        if isinstance(d.itervalues().next(), list):
            raise ValueError('Dictionary must not be a map to list: %r' % d)

        xml_list = ['<?xml version="1.0" encoding="UTF-8" ?>\n']
        xml_list.append(self.__tostring_helper(d))
        return ''.join(xml_list)

    def __tostring_helper(self, d):
        if isinstance(d, int):
            return str(d)
        elif isinstance(d, basestring):
            return '<![CDATA[%s]]>' % d
        elif isinstance(d, dict):
            x = []
            for tag, content in d.iteritems():
                if content is None:
                    x.append('<%s />' % tag)
                elif isinstance(content, list):
                    for c in content:
                        if c is None:
                            x.append('<%s />' % tag)
                        else:
                            x.append('<%s>%s</%s>' %\
                                     (tag, self.__tostring_helper(c), tag))
                else:
                    x.append('<%s>%s</%s>' %\
                             (tag, self.__tostring_helper(content), tag))
            xml_string = ''.join(x)
            return xml_string
        else:
            raise ValueError('Cannot convert %r to an XML string' % d)