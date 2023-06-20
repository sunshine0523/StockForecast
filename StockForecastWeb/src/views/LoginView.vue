<template>
  <div class="login-header-div"/>
  <el-row>
    <el-col :span="16">
      <div class="login-img-div">
        <el-image :src="loginImg" fit="fill" />
      </div>
    </el-col>
    <el-col :span="8">
      <el-card>
        <h2 class="login-title">登录</h2>
        <el-form
          label-position="top"
          :model="userInfo"
        >
          <el-form-item label="大模型提供商">
            <el-select v-model="userInfo.type" placeholder="选择大模型提供商" style="width: 100%" size="large">
              <el-option label="OpenAI" :value="0"/>
              <el-option label="Azure OpenAI" :value="1"/>
            </el-select>
          </el-form-item>
          <el-form-item label="终结点" size="large">
            <el-input v-model="userInfo.endpoint" placeholder="输入终结点"/>
          </el-form-item>
          <el-form-item label="部署模型" size="large">
            <el-input v-model="userInfo.deploymentOrModel" placeholder="输入部署模型"/>
          </el-form-item>
          <el-form-item label="密钥" size="large">
            <el-input v-model="userInfo.key" type="password" placeholder="输入密钥" show-password/>
          </el-form-item>
        </el-form>
        <el-button
            @click="toLogin"
            class="login-button"
            type="primary"
            size="large"
            :loading="loginLoading"
            :disabled="loginLoading"
        >
          登录
        </el-button>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import axios from "axios";
import baseUrls from "@/config/baseUrlConfig";
import {ElMessage} from "element-plus";
import { useRouter } from 'vue-router'
import loginImg from '@/assets/img/login.svg'

const router = useRouter()

const loginLoading = ref(false)

const userInfo = reactive({
  type: 0,
  endpoint: '',
  deploymentOrModel: '',
  key: ''
})

const toLogin = () => {
  loginLoading.value = true
  axios.post(
      `${baseUrls.semantic_kernel_service}/Authentication/authentication`,
      userInfo
  ).then((response) => {
    ElMessage("验证成功")
    localStorage.setItem("token", response.data.token)
    document.location.href='/'
  }).catch((e) => {
    ElMessage("验证失败" + e)
  }).finally(()=>{
    loginLoading.value = false
  })
}
</script>

<style scoped lang="sass">
.login-title
  text-align: center
  margin: 6px 0
  font-weight: bold

.login-button
  width: 100%
  margin: 6px 0

.login-img-div
  display: flex
  justify-content: space-between
  align-items: center
  width: 70%
  height: 70%
  margin: 5% 15% 0 15%

.login-header-div
  position: absolute
  background-image: linear-gradient(to top, #ffffff, #c9cad7, #9299b2, #576b8d, #03426a)
  left: 0
  top: 0
  width: 100%
  height: 200px
  z-index: -1

.el-card
  border-radius: 16px

::v-deep .el-input__wrapper
  border-radius: 32px

.el-button
  border-radius: 32px
</style>