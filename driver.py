import iq_init


def query(sql_query: str):
    return iq_init.__linker__(sql_query)
