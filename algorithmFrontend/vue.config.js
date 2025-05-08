const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    historyApiFallback: true,
    hot: true,
    client: {
      overlay: true
    }
  },
  publicPath: '/',
  configureWebpack: {
    devtool: 'source-map'
  }
})
