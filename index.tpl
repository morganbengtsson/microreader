<html>
<head>
	<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>

	<style type="text/css">
		body
		{
			font-family: sans-serif;
			font-size: 0.8em;
			line-height: 1.2em;
			margin: 0;
			padding: 0;
			position: relative;
		}
		a
		{
			text-decoration: none;
			color: #003C7D;
		}
		dl, dt, dd, ul, li
        {
			margin: 0;
			padding: 0;
		}    
        dt
        { 
			cursor: hand; cursor: pointer; 
		}        
		#left
		{
			width: 140px;
			height: 100%;
			background-color: e1e1e1;
			position: absolute;
			border-right: 1px solid grey;
		}
		#right
		{
			margin-left: 140px;
			max-width: 600px;
			position: relative;		
		}
		.channel, .item
		{
			margin-top: 0;
            margin-bottom: 0;
            padding-top: 0.4em;
            padding-bottom: 0.5em;
            padding-left: 0.5em;
		}
		.item
		{
			overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;            
                       
		}
		.item_wrap
		{
			border-bottom: 1px solid grey; 
		}
		.title 
		{				
			font-size: 100%;
			margin: 0;
			padding: 0;
			font-weight: bold;
			display: inline;						
		}
		.summary
		{			
			color: grey;
			display: inline;
        } 
        .description
        {
			padding: 0.8em;			
		}
        .active
        {
			color: #820000;
		}
				
	</style>
</head>
<body>
	<nav id = "left">
		<ul>
		%for channel in channels:		
			<li class = "channel">				
				<a href = "/{{channel['url']}}" class = "{{"active" if (channel['url'] == url) else ""}}">
					<h2 class="title">{{channel['title']}}</h2> 
				</a>			
			</li>		
		%end
		</li>	
	</nav>
	<dl class = "accordion" id = "right">
		%for item in items:
		<div class = "item_wrap">
		<dt class = "item">				
			<h2 class="title">{{item['title']}}</title> -
			<span class="summary">
				{{item['description']}}
			</span>			
		</dt>
		<dd class = "description">
			{{item['description']}}
		</dd>
		</div>
		%end	
	</dl>
</body>

</html>
<script>
	$('.accordion dd').hide();
	$('.accordion dt').click(function(){
    cur_stus = $(this).attr('stus');
    if(cur_stus != "active")
    {
        $('.accordion dd').hide();
        $('.accordion dt').attr('stus', '');
        
        $(this).next().show();
        $(this).attr('stus', 'active');
    }
    return false;
	});
</script>
