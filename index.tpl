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
		nav a
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
		.accordion a
		{
			text-decoration: none;
			color: black;	
		}
		.item_wrap
		{		
				
			border-bottom: 1px solid #e1e1e1; 
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
		.read
		{
			background-color: #F0F0F0;
			color: grey;
		}
				
	</style>
</head>
<body>
	<nav id = "left">
		<ul>
		%for channel in channels:		
			<li class = "channel">				
				<a href = "/{{channel['url']}}">
					<h2 class="title">{{channel['title']}}</h2> 
				</a>			
			</li>		
		%end
		</ul>	
	</nav>
	<dl class = "accordion" id = "right">
		%for item in items:
		<div class = "item_wrap">
		<dt class = "item {{"active" if (channel['url'] == url) else ""}} {{"read" if item['read'] else ""}}">
			<a class = "mark_star" href ="/items/{{item['id']}}">&#9733;</a>
			<a class = "mark_read" href ="/items/{{item['id']}}">			    
				<h2 class="title">{{item['title']}}</h2>
				 -
			<span class="summary">
				{{!item['description']}}
			</span>	
			</a>		
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
	$(document).ready(function()
	{
		$('.accordion dd').hide();	
		$('.item a').click(function(event)
		{
			var item = $(this).parent();
			event.preventDefault();			
			$.ajax({
				url: $(this).attr('href'),				
				data: '{"read" : true}',				
				contentType: "application/json; charset=utf-8",
				type: 'PATCH',
				success: function()
				{					
					item.addClass('read');
				}							
			});
		});
		$('.accordion dt').click(function(event)
		{			
						
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
	});
</script>
