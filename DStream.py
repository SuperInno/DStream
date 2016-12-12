import Header
import Grid
import Helper
import Cluster
import ClusterManager
import GridList
import math



#主类，用于算法的处理
class D_Stream:
    #=================变量声明=======================
    #时间尺度里的当前时间点，初始值是0，之后以整数1为单位推进
    tc=0
    #grid_list，用于存储grid的character_vector的dic
    grid_list=None
    #clusters 类簇的记录表，kv结构，v集合,集合里保存key
    #clusters={}
    #ClusterManager
    cluster_manager=None

    #========以下是函数=================

    #TODO:初始化变量，结构等，做好准备工作
    def __init__(self):
        self.tc=0;
        self.cluster_manager=ClusterManager()
        self.grid_list=GridList()

    #注释:现在直接往cluster里加grid就可以
    # def __addToCluster(self,grid,cluster):
    #     #TODO:加到cluster里
    #     #TODO:更新操作clusters表





    def __adjust_sparse(self,grid_object):
            #把这个grid从cluster中移除
            cluster_object=self.cluster_manager.getCluster(grid_object.key())

            if not cluster_object==None:
                cluster_object.delGrid(grid_object.key())

                #判断被删除grid的cluster有没有被分离成两个cluster若有，进行处理
                if not cluster_object.isClusterSingle():
                    self.cluster_manager.splitCluster(cluster_object.key())
    #=================================================

    def __adjust_dense_neighbor_dense(self,grid_object,grid_h_object):
    #如果g还没有cluster，调用__addToClusters
        if -1==grid_object.clusterKey():
            gird_h_cluster_object=self.cluster_manager.getCluster(grid_h_object.key())
            grid_h_cluster_object.addGrid(grid_object)

        #如果g已经有cluster且他的cluseter比h大，那么吞并h的cluster，否则反向吞并
        elif not -1==grid_object.clusterKey():
            grid_cluster_object=self.cluster_manager.getCluster(grid_object.key())
            grid_h_cluster_object=self.cluster_manager.getCluster(grid_h_object.key())
            if grid_cluster_object.size()>grid_h_cluster_object.size:
                self.cluster_manager.mergeCluster(grid_cluster_object.key(),grid_h_cluster_object.key())
            else:
                self.cluster_manager.mergeCluster(grid_h_cluster_object.key(),grid_cluster_object.key())

    #=================================================

    def __adjust_dense_neighbor_transitional(self):
      #当grid没有cluster时
        if -1==grid_object.clusterKey():

            #拿h的cluster
            grid_h_cluster_object=self.cluster_manager.getCluster(grid_h_object.key())
            grid_h_cluster_object.addGrid(grid_object)
            #把grid加到h的cluster里并判断此时h是不是outside,如果不是再把grid拿出来
            if not grid_h_cluster_object.isOutsideGrid(grid_h_object):
                gird_h_cluster_object.delGrid(grid_object)
        else:
            #grid易主
            if grid_cluster_object.size()>grid_h_cluster_object.size():
                grid_h_cluster_object.delGrid(grid_h_object)
                grid_cluster_object.addGrid(grid_h_object)
    #=================================================


    def __adjust_dense(self,grid_object):
        #得到这个dense grid （暂且叫g）的所有neighboring grid，在所有neighbor中找出cluster最大的一个grid叫grid_h
        neighbors=self.grid_list.getNeighborGrids()
        if 0==len(neighbors):
            continue

        max_size=0
        grid_h_object=None
        for item in neighbors:
            cluster=self.cluster_manager.getCluster(item.key())
            if not None==cluster and cluster.size()>max_size:
                max_size=cluster.size()
                grid_h_object=item


        #如果这个h是一个dense
        if DensityStatus.DENSE==grid_h_object.densityStatus():

            self.__adjust_dense_neighbor_dense()

        #如果g是一个transitinal，
        elif DensityStatus.TRANSITIONAL==grid_h_object.densityStatus():

            self.__adjust_dense_neighbor_transitional()



    #=================================================





    def __adjust_transitional(self,grid_object):

        neighbor_clusters=self.cluster_manager.getNeighborClusters(grid_object)
            #在neighbor的grid中找出一个cluster，这个cluster最大且当g加入以后g师outside
            for cluster in neighbor_clusters:
                the_ret_cluster_key=-1
                the_ret_cluster_size=0
                if cluster.size()>the_ret_cluster_size:
                    if cluster.isOutsideIfAdd(grid_object):
                        the_ret_cluster_size=cluster.size()
                        the_ret_cluster_key=cluster.key()
            #for循环结束就能找到了,当然也可能没有
            if not -1==the_ret_cluster_key && 0==the_ret_cluster_size:
                target=self.cluster_manager.getCluster(the_ret_cluster_key)
                target.addGrid(grid_object)

#=================================================


        #=================================================


    #=================================================

    def initial_clustring(self):
        stop_flag=0 #为0则不停止，为1停止，即一遍循环没有任何class被修改后标记为1
        #在grid_list中找所有是dense的C_Vector，把他们的label按0开始各自设置，并在clusters里记录，其他的非dense的grid设置成no_class
        while 0==stop_flag:
            #标记类簇被改变，若有类簇发生改变则++
            change_flag=0
            #遍历clusters，拿到每个clusters的set
            all_clusters=self.cluster_manager.getAllCluster()
            for cluster in all_clusters:
                #找到属于outside的grid
                outside_grids=cluster.getOutsideGrids()
                for outside_grid in outside_grids:
                    # 对属于outside的grid，获取它的neighboring 的grid
                    neighbor_grids=self.grid_list.getNeighborGrids(outside_grid.key())
                    for neighbor_grid in neighbor_grids:
                        #若outside的grid所在cluster的尺度大于neighboring的grid，则吞并neighboring的cluster，同时change_flag++
                        neighbor_cluster=self.cluster_manager.getCluster(neighbor_grid.key())
                        if not neighbor_cluster==None:
                            if cluster.size()>neighbor_cluster.size():
                                self.cluster_manager.mergeCluster(cluster.key(),neighbor_cluster.key())
                                change_flag+=1
                            else:
                                self.cluster_manager.mergeCluster(neighbor_cluster.key()，cluster.key())
                                change_flag+=1
                        #否则反向吞并，同时change_flag++
                        elif neighbor_grid.densityStatus()==DensityStatus.TRANSITIONAL:
                                cluster.addGrid(neighbor_grid)
                                change_flag+=1
            #while停止
            if not 0==change_flag:
                stop_flag=1

    def adjust_clustring(self):
        #得到一个已经改变过的change_flag==1的数组
        change_grids=self.grid_list.getChangeGrids()
        #遍历这个数组，处理每一个grid的C_Vector
        for grid_object in change_grids:
            # 处理sparse
            if DensityStatus.SPARSE==grid_object.densityStatus():
                self.__adjust_sparse(grid_object)

            #处理dense
            if DensityStatus.DENSE==grid_object.densityStatus():
                self.__adjust_dense(grid_object)

            #处理transitional
            if DensityStatus.TRANSITIONAL==grid_object.densityStatus():
                self.__adjust_transitional(grid_object)









    def do_DStream(self,rawData):
        self.tc+=1
        #得到key值后，我们将数据点打到相应的grid中，然后更新其信息
        self.grid_list.addNewData(rawData)
        #grid_key=Helper.getKeyFromRawData(rawData)
        #判断grid_list里面有没有对应key，没有先添加
        #if not self.grid_list.has_key(grid_key):
            #1、创建新的C_Vector；
            #2、加入grid_list 里；
        #更新grid的信息
        #if not 0==self.__refreshGrid(grid_key,rawData):
           # print("key 不存在，__refreshGrid调用失败\n")

        #TODO:首次到达gap
        if self.tc==gap:
            self.initial_clustring()
        if self.tc%gap==0:
            #判断sporadic的状态并删除符合条件的grid
            self.grid_list.removeSporadic()
            self.adjust_clustring()
        #清空change为0
        self.grid_list.clearChangeFlag()




