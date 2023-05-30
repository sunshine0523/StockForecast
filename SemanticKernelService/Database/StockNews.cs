using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace SemanticKernelService.Database;

[Table("stock_news")]
public class StockNews
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Required] 
    [Column("stock_code")] 
    public string StockCode { get; set; }

    [Required] 
    [Column("time_stamp")] 
    public int TimeStamp { get; set; }
    
    [Required] 
    [Column("news_title")] 
    public string NewsTitle { get; set; }
    
    [Required] 
    [Column("news_content")] 
    public string NewsContent { get; set; }
    
    [Required] 
    [Column("news_link")] 
    public string NewsLink { get; set; }
    
    [Required]
    [Column("emotion")]
    public int Emotion { get; set; }
}