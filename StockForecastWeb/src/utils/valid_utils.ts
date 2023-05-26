export const validLogin = () => {
    return sessionStorage.getItem('isLogin') == '1'
}