#!/usr/bin/env /Applications/Autodesk/maya2019/Maya.app/Contents/bin/mayapy
import sys
print(sys.prefix)
# import os
from os.path import join
# from maya.standalone import initialize
# initialize("python")
#
import maya.cmds as cmds
# cmds.loadPlugin("fbxmaya")

# import maya.mel as mel
import pymel.core as pm
import pymel.core.nodetypes as nt
import maya.api.OpenMaya as om
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='This py script support batch checking maya scenes, \
                                                  exporting to fbx, and renaming meshes')

    parser.add_argument('-check', nargs='+', help='checks maya files, files should be written as absolute paths')
    parser.add_argument('-export', nargs='+', help='export every mesh as fbx, index 0 = directory path, \
                                                   index >0 = abs paths to scenes')
    parser.add_argument('-rename', nargs='+', help='rename meshes in files, index 0 = name to be replaced, \
                                                   index 1 = name to replace with, index >1 = abs paths to scenes')
    parser.add_argument('-prefix', nargs='+', help='add prefix to meshes in files, index 0 = prefix, \
                                                    index >0 = abs paths to scenes')
    parser.add_argument('-suffix', nargs='+', help='add suffix to meshes in files, index 0 = suffix, \
                                                    index >0 = abs paths to scenes')

    # parser.add_argument('-box', action='store_true', help='create a box fbx')

    # test_command = '-export'
    # test_command += ' /Users/ivanyou/Desktop/cis191/mayaTest'
    # test_command += ' /Users/ivanyou/Desktop/cis191/mayaTest/check_test_cube.mb'

    # rename test
    # test_command = '-rename'
    # test_command += ' Cube'
    # test_command += ' happy'
    # test_command += ' /Users/ivanyou/Desktop/cis191/mayaTest/check_test_cube.mb'

    # check test
    # test_command = '-check'
    # test_command += ' /Users/ivanyou/Desktop/cis191/mayaTest/check_test_bad_uv.mb'
    # test_command += ' /Users/ivanyou/Desktop/cis191/mayaTest/check_test.mb'

    # args = parser.parse_args(test_command.split())
    args = parser.parse_args()

    return args


def makeCube():
    """
    this is a test function. creates a cube in the scene
    :return: void
    """
    my_cube = pm.polyCube()[0]
    pm.select( my_cube , r=True )
    pass

def exportFbxTo(dir_path):
    """
    export every mesh as fbx to dir_path
    :param string dir_path: directory path, e.g. "/Users/ivanyou/Desktop/cis191/mayaTest"
    :param string a: string to be replaced
    :param string b: string to replace with
    :return: void
    """
    for mesh in get_all_geo():
        pm.select(mesh, r=True)
        my_filename = mesh.name() + ".fbx"
        my_folder = dir_path
        full_file_path = join(my_folder, my_filename).replace('\\', '/')
        pm.exportSelected(full_file_path)
    pass

def recursive_search_replace(node, a, b):
    """
    recursively change names
    :param pymel.node node: node to search replace name
    :param string a: string to be replaced
    :param string b: string to replace with
    :return: void
    """
    node.rename(node.name().replace(a, b))
    for child in node.getChildren():
        recursive_search_replace(child, a, b)
    pass

def recursive_add_prefix(node, prefix):
    """
    recursively change names
    :param pymel.node node: node to add prefix
    :param string prefix: prefix to append
    :return: void
    """
    node.rename(prefix + node.name())
    for child in node.getChildren():
        recursive_add_prefix(child, prefix)
    pass

def recursive_add_suffix(node, suffix):
    """
    recursively change names
    :param pymel.node node: node to add suffix
    :param string suffix: suffix to append
    :return: void
    """
    node.rename(node.name() + suffix)
    for child in node.getChildren():
        recursive_add_prefix(child, suffix)
    pass

def set_arnold():
    """
    set default renderer to arnold
    :return void:
    """
    if( pm.getAttr( 'defaultRenderGlobals.currentRenderer' ) != 'arnold' ):
        pm.setAttr('defaultRenderGlobals.currentRenderer', 'arnold')
    pass

def get_all_geo():
    """
    return a list of geometry nodes
    :return list[pymel.core.nodetypes.Mesh]:
    """
    all_obj = pm.ls(geometry=True) #Returns a list of all geometry (even nurbs)
    for x in all_obj:
        if type(x) is not nt.Mesh:
            all_obj.remove(x)
    return all_obj #Returns a list of pymel.core.nodetypes.Mesh


def get_all_geo_trans():
    return pm.listRelatives(pm.ls(geometry=True), p=True)


def find_non_manifold_objects():
    """
    Print if there are objects with non-manifold geometry in the scene
    :return:
    """

    print("Finding objects with non-manifold geometry...")
    geometry_list = pm.ls(geometry=True)  # get a list of all geometry nodes in the scene
    nm_list = []

    # check each mesh for non-manifold edges or vertices
    for mesh in geometry_list:
        nm_geom = pm.polyInfo(mesh, nme=True, nmv=True)

        # only keep those that have non-manifold geometry
        if nm_geom:
            nm_list.extend(nm_geom)  # select the actual geometry

    # Print Result
    if nm_list: print("Found: ", nm_list)
    else: print("No non-manifold edges or vertices in the scene.")
    pass

def find_name_duplicates():
    """
    Print if there are duplicate names in the scene
    :return:
    """
    # Look for objects whose names occur more than once
    print("Finding objects with duplicate names...")  # Show what the function is doing
    node_list = pm.ls(type=nt.DagNode)  # get a list of all DAG nodes

    def is_not_uniquely_named(node):
        assert isinstance(node, nt.DagNode)
        return not node.isUniquelyNamed()

    # filter so that only those without unique names remain
    node_list = filter(is_not_uniquely_named, node_list)
    pm.select(node_list)

    # Print Result
    if node_list: print("Found: ", node_list)
    else: print("All objects have unique names.")
    pass


def find_empty_groups(include_cascading=True, remove=False):
    """
    Print if there are empty groups in the scene
    :param bool include_cascading: alternate definition for isEmpty()
    :param bool remove: whether or not to remove empty groups
    :return:
    """
    # Print what the function is doing
    if remove: print("Removing empty groups...")
    else: print("Finding empty groups...")

    # Helper function that decides whether a Transform node is a group or not
    def isGroup(node):
        assert isinstance(node, nt.Transform)
        children = node.getChildren()

        for c in children:
            if not isinstance(c, nt.Transform):
                return False
        return True

    # Get a list of all groups in the scene
    group_list = pm.ls(exactType='transform')
    group_list = filter(isGroup, group_list)

    # include empty groups that have other empty groups as children?
    if include_cascading:
        # The empty group is defined as a group whose children are empty groups
        def isEmpty(group):
            assert isinstance(group, nt.Transform)

            children = group.getChildren()
            # if a child is not an empty group or not a group at all
            for c in children:
                if not isGroup(c) or not isEmpty(c):
                    return False  # this group is not empty
            return True
    else:
        # The empty group is defined as a group that has 0 children
        def isEmpty(group):
            assert isinstance(group, nt.Transform)

            children = group.getChildren()
            return len(children) < 1  # if this group has any children, it's not empty

    group_list = filter(isEmpty, group_list)
    pm.select(group_list)

    # delete the empty groups if specified
    if remove and group_list:
        print("Removed empty groups:\n%s" % group_list)
        pm.delete(group_list)
    elif group_list:
        print("Found empty groups:\n%s" % group_list)
    else:
        print("No empty groups were found!")
    pass

def judge_edge_position(edges_point, edges_point_ju):
    """
    Determine if two edges may intersect
    :param edges_point:
    :param edges_point_ju:
    :return:
    """
    # judge u
    if min(edges_point[0][0], edges_point[1][0]) > max(edges_point_ju[0][0], edges_point_ju[1][0]) or \
            min(edges_point_ju[0][0], edges_point_ju[1][0]) > max(edges_point[0][0], edges_point[1][0]):
        return True
    # judge v
    elif min(edges_point[0][1], edges_point[1][1]) > max(edges_point_ju[0][1], edges_point_ju[1][1]) or\
            min(edges_point_ju[0][1], edges_point_ju[1][1]) > max(edges_point[0][1], edges_point[1][1]):
        return True
    else:
        return False

def get_max_min_uv(face_point):
    """
    get face max uv value and min uv value
    :param face_point: face point uv value
    :return:
    """
    if len(face_point) == 4:
        return min(face_point[0][0], face_point[1][0], face_point[2][0], face_point[3][0]), \
               max(face_point[0][0], face_point[1][0], face_point[2][0], face_point[3][0]), \
               min(face_point[0][1], face_point[1][1], face_point[2][1], face_point[3][1]), \
               max(face_point[0][1], face_point[1][1], face_point[2][1], face_point[3][1])
    elif len(face_point) == 3:
        return min(face_point[0][0], face_point[1][0], face_point[2][0]), \
               max(face_point[0][0], face_point[1][0], face_point[2][0]), \
               min(face_point[0][1], face_point[1][1], face_point[2][1]), \
               max(face_point[0][1], face_point[1][1], face_point[2][1])
    else:
        print("face is not a tri or quad")

def judge_edge(edges_point, edges_point_ju):
    """
    judge edge intersect
    :param list edges_point: edges point uv value
    :param list edges_point_ju: edges point uv value
    :return: bool
    """

    x1 = edges_point[0][0] - edges_point[1][0]
    y1 = edges_point[0][1] - edges_point[1][1]

    x2 = edges_point_ju[0][0] - edges_point[1][0]
    y2 = edges_point_ju[0][1] - edges_point[1][1]

    x3 = edges_point_ju[1][0] - edges_point[1][0]
    y3 = edges_point_ju[1][1] - edges_point[1][1]

    x4 = edges_point_ju[0][0] - edges_point_ju[1][0]
    y4 = edges_point_ju[0][1] - edges_point_ju[1][1]

    x5 = edges_point[0][0] - edges_point_ju[1][0]
    y5 = edges_point[0][1] - edges_point_ju[1][1]

    x6 = edges_point[1][0] - edges_point_ju[1][0]
    y6 = edges_point[1][1] - edges_point_ju[1][1]

    if (x1 * y2 - x2 * y1) * (x1 * y3 - x3 * y1) < 0.0 and (x4 * y5 - x5 * y4) * (x4 * y6 - x6 * y4) < 0.0:
        return True
    else:
        return False

def judge_face_position(edges_point, edges_point_ju):
    """
    Determine if two faces may intersect
    :param tuple edges_point: edges point uv value
    :param tuple edges_point_ju: edges point uv value
    :return:
    """
    if edges_point[0] >= edges_point_ju[1] or \
            edges_point_ju[0] >= edges_point[1] or \
            edges_point[2] >= edges_point_ju[3] or \
            edges_point_ju[2] >= edges_point[3]:
        return True
    elif (edges_point[0] == edges_point_ju[0] and edges_point[1] == edges_point_ju[1]) and \
            (edges_point[2] == edges_point_ju[2] and edges_point[3] == edges_point_ju[3]):

        return True
    else:
        return False

def find_overlapping_uv_for_mesh(mesh_name):
    """
    check overlapping uv
    :param str mesh_name : object long name eg.'|group3|pSphere1'
    :return: mesh face list
    :rtype: list
    """
    # get MFnMesh
    select_list = om.MSelectionList()
    select_list.add(mesh_name)
    dag_path = select_list.getDagPath(0)
    mfn_mesh = om.MFnMesh(dag_path)

    face_id_over = []   # store overlapping face
    all_uv_value_dict = {}   # store all uv value on the face
    max_min_uv_dict = {}   # store all uv max and min value on the face
    face_edges_dict = {}   # Store all edges on the face

    for face_id in range(mfn_mesh.numPolygons):
        face_edges_dict[face_id] = []
        uv_value_list = []
        for point_index in range(len(mfn_mesh.getPolygonVertices(face_id))):
            uv_value_list.append(mfn_mesh.getPolygonUV(face_id, point_index))

        all_uv_value_dict[face_id] = uv_value_list
        max_min_uv_dict[face_id] = get_max_min_uv(uv_value_list)
        for i in range(len(uv_value_list)):
            if i == len(uv_value_list) - 1:
                edges_value = [(uv_value_list[i][0], uv_value_list[i][1]), (uv_value_list[0][0], uv_value_list[0][1])]
            else:
                edges_value = [(uv_value_list[i][0], uv_value_list[i][1]), (uv_value_list[i + 1][0], uv_value_list[i+1][1])]

            face_edges_dict[face_id].append(edges_value)

    for face_id in range(mfn_mesh.numPolygons):

        edges_list = face_edges_dict[face_id]
        for face_id_next in range(face_id + 1, mfn_mesh.numPolygons):
            have = 0   # if edges intersect 'have is 1'
            edg_list_next = face_edges_dict[face_id_next]

            if not judge_face_position(max_min_uv_dict[face_id], max_min_uv_dict[face_id_next]):

                for edges_point in edges_list:
                    if have == 0:
                        for edg_point_ju in edg_list_next:

                            if not judge_edge_position(edges_point, edg_point_ju):

                                if judge_edge(edges_point, edg_point_ju):

                                    if face_id not in face_id_over:
                                        have = 1
                                        face_id_over.append(face_id)
                                    if face_id_next not in face_id_over:
                                        have = 1
                                        face_id_over.append(face_id_next)

                                    break
                    else:
                        break

    return ['{0}.f[{1}]'.format(mesh_name, face_id_num) for face_id_num in face_id_over]

def find_overlapping_uv():
    """
    Print if there are meshes with overlapping uv in the scene
    :return:
    """
    meshes_with_overlapping_uv = []

    for mesh in get_all_geo():
        res = find_overlapping_uv_for_mesh(mesh.name())
        if len(res) > 0:
            meshes_with_overlapping_uv.append(mesh.name())

    if len(meshes_with_overlapping_uv) > 0:
        for mesh_name in meshes_with_overlapping_uv:
            print(mesh_name + " has overlapping uv")
    else:
        print("no meshes with overlapping uv")
    pass

if __name__ == '__main__':
    args = parse_args()

    if args.check is not None and len(args.check) > 0:
        for scene_path in args.check:
            print("=====checking " + scene_path + "=====")
            cmds.file(new=True, force=True)
            cmds.file(scene_path, open=True)
            find_non_manifold_objects()
            find_name_duplicates()
            find_empty_groups()
            find_overlapping_uv()
        print("finished check operation")

    if args.export is not None and len(args.export) > 1:
        dir_path = args.export[0]
        for i in range(1, len(args.export)):
            scene_path = args.export[i]
            cmds.file(new=True, force=True)
            cmds.file(scene_path, open=True)
            exportFbxTo(dir_path)
            print("finished exporting " + scene_path)
        print("finished export operation")

    if args.rename is not None and len(args.rename) >= 3:
        a = args.rename[0]
        b = args.rename[1]
        for i in range(2, len(args.rename)):
            scene_path = args.rename[i]
            cmds.file(new=True, force=True)
            cmds.file(scene_path, open=True)
            for mesh in get_all_geo_trans():
                recursive_search_replace(mesh, a, b)
            cmds.file(save=True, force=True, type="mayaBinary")
        print("finished rename operation")

    if args.prefix is not None and len(args.prefix) >= 2:
        prefix = args.prefix[0]
        for i in range(1, len(args.prefix)):
            scene_path = args.prefix[i]
            cmds.file(new=True, force=True)
            cmds.file(scene_path, open=True)
            for mesh in get_all_geo_trans():
                recursive_add_prefix(mesh, prefix)
            cmds.file(save=True, force=True, type="mayaBinary")
        print("finished prefix operation")

    if args.suffix is not None and len(args.suffix) >= 2:
        suffix = args.suffix[0]
        for i in range(1, len(args.suffix)):
            scene_path = args.suffix[i]
            cmds.file(new=True, force=True)
            cmds.file(scene_path, open=True)
            for mesh in get_all_geo_trans():
                recursive_add_suffix(mesh, suffix)
            cmds.file(save=True, force=True, type="mayaBinary")
        print("finished suffix operation")

    pass