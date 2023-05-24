// Copyright (c) Microsoft. All rights reserved.

using System.Collections.Generic;
using System.Linq;

namespace SemanticKernelService.Model;

public class Ask
{
    public string Value { get; set; } = string.Empty;

    public IEnumerable<AskInput> Inputs { get; set; } = Enumerable.Empty<AskInput>();
}

public class AskInput
{
    public string Key { get; set; } = string.Empty;

    public string Value { get; set; } = string.Empty;
}
