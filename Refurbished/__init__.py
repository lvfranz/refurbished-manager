# Support for PyMySQL as MySQLdb alternative (useful on Windows)
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

