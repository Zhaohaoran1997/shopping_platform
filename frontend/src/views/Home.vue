<template>
  <div class="home-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-carousel height="400px">
          <el-carousel-item v-for="item in 4" :key="item">
            <div class="carousel-content">
              <h3>促销活动 {{ item }}</h3>
            </div>
          </el-carousel-item>
        </el-carousel>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="feature-section">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>热门商品</span>
              <el-button class="button" text>查看更多</el-button>
            </div>
          </template>
          <div v-for="o in 4" :key="o" class="text item">
            {{ '热门商品 ' + o }}
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>新品上架</span>
              <el-button class="button" text>查看更多</el-button>
            </div>
          </template>
          <div v-for="o in 4" :key="o" class="text item">
            {{ '新品 ' + o }}
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>特价商品</span>
              <el-button class="button" text>查看更多</el-button>
            </div>
          </template>
          <div v-for="o in 4" :key="o" class="text item">
            {{ '特价商品 ' + o }}
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.home-container {
  padding: 20px;
}

.carousel-content {
  height: 100%;
  background-color: #d3dce6;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #fff;
  font-size: 24px;
}

.feature-section {
  margin-top: 40px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text {
  font-size: 14px;
}

.item {
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.item:last-child {
  border-bottom: none;
}
</style> 