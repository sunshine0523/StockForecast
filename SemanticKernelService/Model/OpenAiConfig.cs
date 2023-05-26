namespace SemanticKernelService.Model;

public class OpenAiConfig
{
    public OpenAiType Type { get; set; }
    public string Endpoint { get; set; }
    public string DeploymentOrModel { get; set; }
    public string Key { get; set; }
}

public enum OpenAiType
{
    OpenAi,
    AzureOpenAi
}