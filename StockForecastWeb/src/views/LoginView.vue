<template>
  <el-row>
    <el-col :span="16"/>
    <el-col :span="8">
      <el-card>
        <h2 class="login-title">登录</h2>
        <el-form
          label-position="top"
          :model="userInfo"
        >
          <el-form-item label="大模型提供商">
            <el-select v-model="userInfo.type" placeholder="选择大模型提供商" style="width: 100%" size="large">
              <el-option label="OpenAI" value="1"/>
              <el-option label="Azure OpenAI" value="2"/>
            </el-select>
          </el-form-item>
          <el-form-item label="终结点" size="large">
            <el-input v-model="userInfo.endpoint" placeholder="输入终结点"/>
          </el-form-item>
          <el-form-item label="部署模型" size="large">
            <el-input v-model="userInfo.deployment" placeholder="输入部署模型"/>
          </el-form-item>
          <el-form-item label="密钥" size="large">
            <el-input v-model="userInfo.key" placeholder="输入密钥"/>
          </el-form-item>
        </el-form>
        <el-button
            @click="toLogin"
            class="login-button"
            type="primary"
            size="large"
        >
          登录
        </el-button>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { reactive } from "vue";
import axios from "axios";

const userInfo = reactive({
  type: '',
  endpoint: '',
  deployment: '',
  key: ''
})

const toLogin = () => {
  axios
}
</script>

<style scoped>
.login-title {
  text-align: center;
  margin: 6px 0;
}
.login-button {
  width: 100%;
  margin: 6px 0;
}
</style>