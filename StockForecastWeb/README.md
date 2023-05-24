# web

前端使用Vue3。使用的库安装步骤：

注意：正常情况下只需在项目目录下执行npm install即可，无需下列库安装步骤！

- 初始化vue项目

```shell
npm init vue@latest
```

在初始化时，需要选择ts和vue router

- element-plus

```shell
npm install element-plus --save
```

- 自动导入element组件插件

```shell
npm install -D unplugin-vue-components unplugin-auto-import --save-dev
```

```ts
//配置部分
// vite.config.ts
import { defineConfig } from 'vite'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
    // ...
    plugins: [
        // ...
        AutoImport({
            resolvers: [ElementPlusResolver()],
        }),
        Components({
            resolvers: [ElementPlusResolver()],
        }),
    ],
})
```

- element-plus/icons-vue

```shell
npm install @element-plus/icons-vue --save
```

- 自动导入element-plus/icons-vue插件

```shell
npm install -D unplugin-icons --save-dev
npm install -D unplugin-auto-import --save-dev
```

注意，自动导入图标需要加前缀i-ep：
```vue
<template>
  <!--如需要导入edit图标，需要：-->
  <i-ep-edit/>
</template>
```

```ts
//配置部分
//vite.config.ts
import path from 'path'
import { defineConfig } from 'vite'
import Vue from '@vitejs/plugin-vue'
import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import Inspect from 'vite-plugin-inspect'

const pathSrc = path.resolve(__dirname, 'src')

export default defineConfig({
    resolve: {
        alias: {
            '@': pathSrc,
        },
    },
    plugins: [
        Vue(),
        AutoImport({
            // Auto import functions from Vue, e.g. ref, reactive, toRef...
            // 自动导入 Vue 相关函数，如：ref, reactive, toRef 等
            imports: ['vue'],

            // Auto import functions from Element Plus, e.g. ElMessage, ElMessageBox... (with style)
            // 自动导入 Element Plus 相关函数，如：ElMessage, ElMessageBox... (带样式)
            resolvers: [
                ElementPlusResolver(),

                // Auto import icon components
                // 自动导入图标组件
                IconsResolver({
                    prefix: 'Icon',
                }),
            ],

            dts: path.resolve(pathSrc, 'auto-imports.d.ts'),
        }),

        Components({
            resolvers: [
                // Auto register icon components
                // 自动注册图标组件
                IconsResolver({
                    enabledCollections: ['ep'],
                }),
                // Auto register Element Plus components
                // 自动导入 Element Plus 组件
                ElementPlusResolver(),
            ],

            dts: path.resolve(pathSrc, 'components.d.ts'),
        }),

        Icons({
            autoInstall: true,
        }),

        Inspect(),
    ],
})
```

- sass

```shell
npm install -D sass --save-dev
```

- axios

```shell
npm install axios --save
```

- socket-io

```shell
npm install socket.io-client --save
```