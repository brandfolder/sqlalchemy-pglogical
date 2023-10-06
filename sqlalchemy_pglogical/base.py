def ddl_to_replicate_command(ddl: str) -> str:
    """
    Given a DDL command as a string, return a pglogical replicate command for that DDL
    """
    # TODO: allow specifying the replication sets
    return f"""SELECT pglogical.replicate_ddl_command($sqlalchemypglogical$
    {ddl}
    $sqlalchemypglogical$)"""
