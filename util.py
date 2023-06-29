import asyncio


def is_true_complex(val) -> bool:
    return isinstance(val, bool) and val \
        or isinstance(val, int) and val > 0 \
        or isinstance(val, float) and val > 0 \
        or str(val).lower() == 't' \
        or str(val).lower() == 'true' \
        or str(val).lower() == 'y' \
        or str(val).lower() == 'yes'


def run_sync(coroutine):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coroutine)


def uri_to_path(uri: str) -> str:
    if uri.startswith('file://'):
        return uri.removeprefix('file://')
    else:
        raise Exception('Unsupported uri type!\nFile:"' + uri + '"')


def course_code(section_id: str, prefix: str, semester: int) -> str:
    section_id_suffix = '-' + section_id.split('-')[-1]
    return prefix \
        + section_id.removesuffix(section_id_suffix) \
        + '-S' + str(semester)


def section_id_header(i: int):
    return 'Section ID (' + str(i) + ') - Classes Cluster'


def section_number_header(i: int):
    return 'Section Number (' + str(i) + ') - Classes Cluster'


def faculty_id_primary_header(i: int):
    return 'Faculty ID (Primary) (' + str(i) + ') - Classes Cluster'


def faculty_name_primary_header(i: int):
    return 'Faculty Name (Primary) (' + str(i) + ') - Classes Cluster'
