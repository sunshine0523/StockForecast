using Microsoft.SemanticKernel;
using SemanticKernelService.Database;
using SemanticKernelService.Model;

namespace SemanticKernelService.Services;

public interface IAuthenticationService
{
    public Task<ValidResult> ToValidOpenAiAsync(OpenAiConfig param);
    public void AddLoginUser(string token, OpenAiConfig openAiConfig, string mysqlConnectionString, ILogger logger);
    public string ToValidToken(string token);
}

public enum ValidResult
{
    SUCCESS,
    FAIL
}