using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace SemanticKernelService.Database;

[Table("news_emotion")]
public class NewsEmotion
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Required] 
    [Column("stock_code")] 
    public string StockCode { get; set; }

    [Required] 
    [Column("news_time")] 
    public string NewsTime { get; set; }
    
    [Required] 
    [Column("emotion")] 
    public string Emotion { get; set; }
}