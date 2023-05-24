namespace SemanticKernelService.Model;

public class UserTokenInfo
{
    public UserTokenInfo(string token)
    {
        Token = token;
    }
    public string Token { get; set; }
}