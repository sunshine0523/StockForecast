using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.CoreSkills;
using Microsoft.SemanticKernel.Skills.Document;
using Microsoft.SemanticKernel.Skills.Document.FileSystem;
using Microsoft.SemanticKernel.Skills.Document.OpenXml;
using Microsoft.SemanticKernel.Skills.Web;
using Microsoft.SemanticKernel.TemplateEngine;
using MongoDB.Bson;
using SemanticKernelService.Database;
using SemanticKernelService.Model;
using SemanticKernelService.Skills.Native.Stock;
using SemanticKernelService.Skills.Native.StockDb;

namespace SemanticKernelService.Utils;

internal static class SemanticKernelFactory
{
    internal static IKernel CreateKernel(
        OpenAiConfig param,
        string mysqlConnectionString,
        ILogger logger)
    {
        KernelBuilder builder = Kernel.Builder;
        builder = _ConfigureKernelBuilder(param, builder);
        return _CompleteKernelSetup(builder, mysqlConnectionString, logger);
    }

    private static KernelBuilder _ConfigureKernelBuilder(OpenAiConfig param, KernelBuilder builder)
    {
        return builder.Configure(c =>
        {
            switch (param.Type)
            {
                case OpenAiType.OpenAi:
                    c.AddOpenAIChatCompletionService(
                        modelId: param.DeploymentOrModel!,
                        apiKey: param.Key!,
                        serviceId: "sunshine");
                    break;
                case OpenAiType.AzureOpenAi:
                    c.AddAzureChatCompletionService(
                        deploymentName: param.DeploymentOrModel!,
                        endpoint: param.Endpoint!,
                        apiKey: param.Key!,
                        serviceId: "sunshine",
                        alsoAsTextCompletion: true);
                    break;
            }
        });
    }

    private static IKernel _CompleteKernelSetup(KernelBuilder builder, string mysqlConnectionString, ILogger logger)
    {
        IKernel kernel = builder.Build();
        kernel.RegisterSemanticSkills(Directory.GetCurrentDirectory() + "\\Skills\\Semantic", logger);
        kernel.RegisterNativeSkills(mysqlConnectionString, logger);

        return kernel;
    }

    private static void RegisterNativeSkills(this IKernel kernel, string mysqlConnectionString, ILogger logger)
    {
        // DocumentSkill documentSkill = new(new WordDocumentConnector(), new LocalFileSystemConnector());
        // kernel.ImportSkill(documentSkill, nameof(DocumentSkill));
        //
        // ConversationSummarySkill conversationSummarySkill = new(kernel);
        // kernel.ImportSkill(conversationSummarySkill, nameof(ConversationSummarySkill));
        //
        // var webFileDownloadSkill = new WebFileDownloadSkill();
        // kernel.ImportSkill(webFileDownloadSkill, nameof(WebFileDownloadSkill));

        StockDbSkill stockDbSkill = new(kernel, mysqlConnectionString, logger);
        StockSkill stockSkill = new(kernel, stockDbSkill, logger);
        kernel.ImportSkill(stockSkill, nameof(StockSkill));
    }

    private static void RegisterSemanticSkills(
        this IKernel kernel,
        string skillsFolder,
        ILogger logger)
    {
        foreach (string skPromptPath in Directory.EnumerateFiles(skillsFolder, "*.txt", SearchOption.AllDirectories))
        {
            FileInfo fInfo = new(skPromptPath);
            DirectoryInfo? currentFolder = fInfo.Directory;

            while (currentFolder?.Parent?.FullName != skillsFolder)
            {
                currentFolder = currentFolder?.Parent;
            }

            try
            {
                _ = kernel.ImportSemanticSkillFromDirectory(skillsFolder, currentFolder.Name);
            }
            catch (TemplateException e)
            {
                logger.LogError("Could not load skill from {0} with error: {1}", currentFolder.Name, e.Message);
            }
        }
    }

}