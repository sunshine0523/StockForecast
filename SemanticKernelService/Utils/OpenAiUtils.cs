using System.Net;
using SemanticKernelService.Model;
using SemanticKernelService.Services;

namespace SemanticKernelService.Utils;

internal static class OpenAiUtils
{
    // HttpClient lifecycle management best practices:
    // https://learn.microsoft.com/dotnet/fundamentals/networking/http/httpclient-guidelines#recommended-use
    private static readonly HttpClient SharedClient = new();
    internal static async Task<ValidResult> ToValidOpenAiAsync(OpenAiConfig param)
    {
        switch (param.Type)
        {
            case OpenAiType.OpenAi:
                //Not support yet
                return ValidResult.FAIL;
            case OpenAiType.AzureOpenAi:
                var url = param.Endpoint + "/openai/deployments/" + param.DeploymentOrModel + "?api-version=2022-12-01";
                //需要先Remove掉再添加，因为如果已经存在则无法添加
                SharedClient.DefaultRequestHeaders.Remove("api-key");
                SharedClient.DefaultRequestHeaders.Add("api-key", param.Key);
                var result = await SharedClient.GetAsync(url);
                if (result.StatusCode == HttpStatusCode.OK)
                {
                    return ValidResult.SUCCESS;
                }

                return ValidResult.FAIL;
            default:
                //Not support yet
                return ValidResult.FAIL;
        }
    }
}