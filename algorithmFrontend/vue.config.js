const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  // 添加开发服务器配置，确保所有路由都能正确处理
  devServer: {
    historyApiFallback: true,
    hot: true,
    client: {
      overlay: true
    }
  },
  // 设置为相对路径，避免资源加载问题
  publicPath: '/',
  // 启用源映射
  configureWebpack: {
    devtool: 'source-map'
  }
})
