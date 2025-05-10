#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# merge indexed polygon tags, for example glass, glass (2), glass (3) etc.
# ================================

import re
from typing import Iterable

import lx
import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_debug import h3dd, prints, fn_in, fn_out


def main():
    meshes: list[modo.Mesh] = modo.Scene().items(itype=c.MESH_TYPE)  # type: ignore
    geometry_ptags = get_geometry_ptags(meshes)
    merged_ptags: dict[str, list[str]] = dict()

    for geo_ptag in geometry_ptags:
        merged_ptag = get_merged_ptag(geo_ptag)
        if merged_ptag not in merged_ptags:
            merged_ptags[merged_ptag] = [geo_ptag,]
        else:
            merged_ptags[merged_ptag].append(geo_ptag)

    if not merged_ptags:
        return

    prints(merged_ptags)

    for mesh in meshes:
        mesh.select()

    for merged_ptag in merged_ptags:
        prints(merged_ptag)
        tags = merged_ptags[merged_ptag]
        prints(tags)
        tags.sort(key=len)
        prints(tags)
        duplicated_tags = tags[1:]
        prints(duplicated_tags)

        duplicated_masks = get_masks_by_tags(duplicated_tags)
        modo.Scene().removeItems(duplicated_masks, children=True)

        prime_masks = get_masks_by_tags(tags[:1])
        modo.Scene().removeItems(prime_masks[1:], children=True)

        for oldtag in tags:
            rename_tag(oldtag, merged_ptag)


def get_geometry_ptags(meshes: Iterable[modo.Item]) -> set[str]:
    ptags = set()
    for mesh in meshes:
        for poly in mesh.geometry.polygons:  # type: ignore
            ptags.add(poly.materialTag)

    return ptags


def get_merged_ptag(ptag: str) -> str:
    pattern = r'^(.*?)[._ (d)]*[ ().\d]*\d*\)?$'
    match = re.search(pattern, ptag)

    if not match:
        return ptag

    if not match.groups():
        return ptag

    return match.group(1)


def get_masks_by_tags(tags: Iterable[str]) -> tuple[modo.Item, ...]:
    fn_in()
    prints(tags)
    if not tags:
        fn_out('not tags')
        return ()

    filtered_masks: list[modo.Item] = list()
    masks = modo.Scene().items(itype=c.MASK_TYPE)
    if not masks:
        fn_out('not masks')
        return ()

    for mask in masks:
        prints(mask)
        if not is_material_ptyp(get_ptag_type(mask)):
            prints('mask not material ptyp')
            continue

        if get_ptag(mask) not in tags:
            prints(f'{get_ptag(mask)} not in tags')
            continue

        filtered_masks.append(mask)

    fn_out()
    return tuple(filtered_masks)


def get_shadertree_masks() -> set[modo.Item]:
    return set(modo.Scene().items(itype=c.MASK_TYPE))


def rename_tag(old: str, new: str):
    fn_in()
    prints(old)
    prints(new)
    lx.eval(f'poly.renameMaterial {{{old}}} {{{new}}}')
    fn_out()


def get_ptag_type(mask_item: modo.Item) -> str:
    ptyp: str = mask_item.channel('ptyp').get()  # type: ignore
    if not ptyp:
        return 'Material'
    return ptyp


def get_ptag(mask_item: modo.Item) -> str:
    ptag: str = mask_item.channel('ptag').get()  # type: ignore
    return ptag


def is_material_ptyp(ptyp):
    if ptyp == 'Material':
        return True
    if ptyp == '':
        return True

    return False


if __name__ == '__main__':
    h3dd.enable_debug_output()
    main()
