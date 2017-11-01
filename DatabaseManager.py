import logging
import ConfigParser
import MySQLdb, MySQLdb.cursors
import sys


class DatabaseManager(object):
    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read('hass.conf')
        self.db_conn = None
        self.db = None
        try:
            self.connect()
        except MySQLdb.Error, e:
            logging.error("Hass AccessDB - connect to database failed (MySQL Error: %s)", str(e))
            print "MySQL Error: %s" % str(e)
            sys.exit(1)

    def connect(self):
        self.db_conn = MySQLdb.connect(  host = self.config.get("mysql", "mysql_ip"),
                                         user = self.config.get("mysql", "mysql_username"),
                                        passwd = self.config.get("mysql", "mysql_password"),
                                        db = self.config.get("mysql", "mysql_db"),
                                    )
        self.db = self.db_conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

    def createTable(self):
        try:
            self.db.execute("SET sql_notes = 0;")
            self.db.execute("""
                            CREATE TABLE IF NOT EXISTS ha_cluster 
                            (
                            cluster_uuid char(36),
                            cluster_name char(18),
                            PRIMARY KEY(cluster_uuid)
                            );
                            """)
            self.db.execute("""
                            CREATE TABLE IF NOT EXISTS ha_node 
                            (
                            node_name char(18),
                            below_cluster char(36),
                            PRIMARY KEY(node_name),
                            FOREIGN KEY(below_cluster)
                            REFERENCES ha_cluster(cluster_uuid)
                            ON DELETE CASCADE
                            );
                            """)
        except MySQLdb.Error, e:
            self.closeDB()
            logging.error("Hass AccessDB - Create Table failed (MySQL Error: %s)", str(e))
            print "MySQL Error: %s" % str(e)
            sys.exit(1)

    def syncFromDB(self):
        try:
            self.db.execute("SELECT * FROM ha_cluster;")
            ha_cluster_date = self.db.fetchall()
            exist_cluster = []
            for cluster in ha_cluster_date:
                node_list = []
                self.db.execute("SELECT * FROM ha_node WHERE below_cluster = '%s'" % cluster["cluster_uuid"])
                ha_node_date = self.db.fetchall()

                for node in ha_node_date:
                    node_list.append(node["node_name"])
                #cluster_id = cluster["cluster_uuid"][:8]+"-"+cluster["cluster_uuid"][8:12]+"-"+cluster["cluster_uuid"][12:16]+"-"+cluster["cluster_uuid"][16:20]+"-"+cluster["cluster_uuid"][20:]
                cluster_id = cluster["cluster_uuid"]
                cluster_name = cluster["cluster_name"]
                exist_cluster.append({"cluster_id": cluster_id, "cluster_name": cluster_name, "node_list": node_list})
                #cluster_manager.createCluster(cluster_name = name , cluster_id = cluster_id)
                #cluster_manager.addNode(cluster_id, node_list)
            logging.info("Hass AccessDB - Read data success")
            return exist_cluster

        except MySQLdb.Error, e:
            self.closeDB()
            logging.error("Hass AccessDB - Read data failed (MySQL Error: %s)", str(e))
            print "MySQL Error: %s" % str(e)
            sys.exit(1)

    def syncToDB(self, cluster_list):
        self.resetAll()
        try:
            #cluster_list = cluster_manager.getClusterList()
            for cluster_id , cluster in cluster_list.items():
                # sync cluster
                data = {"cluster_uuid":cluster_id, "cluster_name":cluster.name}
                self.writeDB("ha_cluster", data)
                # sync node
                node_list = cluster.getNodeList()
                for node in node_list:
                    data = {"node_name": node.name,"below_cluster":node.cluster_id}
                    self.writeDB("ha_node", data)
        except MySQLdb.Error, e:
            self.closeDB()
            logging.error("Hass database manager - sync data failed (MySQL Error: %s)", str(e))
            print "MySQL Error: %s" % str(e)
            sys.exit(1)

    def writeDB(self , dbName , data):
        if dbName == "ha_cluster":
            format = "INSERT INTO ha_cluster (cluster_uuid,cluster_name) VALUES (%(cluster_uuid)s, %(cluster_name)s);"
        else:
            format = "INSERT INTO ha_node (node_name,below_cluster) VALUES (%(node_name)s, %(below_cluster)s);"
        try:
            self.db.execute(format, data)
            self.db_conn.commit()
        except Exception as e:
            logging.error("Hass AccessDB - write data to DB Failed (MySQL Error: %s)", str(e))
            print "MySQL Error: %s" % str(e)
            raise

    def _getAllTable(self):
        table_list = []
        cmd = "show tables"
        self.db.execute(cmd)
        res = self.db.fetchall() #({'Tables_in_hass': 'talbe1'}, {'Tables_in_hass': 'table2'})
        index = "Tables_in_%s" % self.config.get("mysql", "mysql_db")
        for table in res:
            table_list.append(table[index])
        return table_list

    def resetAll(self):
        table_list = self._getAllTable()
        for table in table_list:
            self._resetTable(table)

    def _resetTable(self, table_name):
        cmd = " DELETE FROM  `%s` WHERE true" % table_name
        self.db.execute(cmd)
        self.db_conn.commit()


    def closeDB(self):
        self.db.close()
        self.db_conn.close()


if __name__ == "__main__":
    a = DatabaseManager()
    print a.resetAll()
