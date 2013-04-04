<html>
<head>
	<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
	<link rel="stylesheet" type="text/css" href="/static/style.css">	
</head>
<body>
	<nav>
		<button id ="add">Subscribe</button>
		<form style ="display:none">
			Url: <input type="text" name = "url" class="url"/>
			<input type="submit" value = "Add">
		</form>
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
	<dl class = "accordion" id = "content">
		%for item in items:
		<div class = "item">			
		<dt class = "{{"active" if (channel['url'] == url) else ""}} {{"read" if item['read'] else ""}}">			
			<div class = "side">12:00 <a class = "link" href = "{{item['url']}}"></a></div>
			<div class = "header">
				<a class = "mark_favorite" href ="/items/{{item['id']}}">bla</a>
							
				<a class = "mark_read" href ="/items/{{item['id']}}">		    
					<h2 class="title">{{item['title']}}</h2>
					 -
				<span class="summary">
					{{!item['description']}}
				</span>
				</a>
			</div>
						
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
		$('.item .mark_read').click(function(event)
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
		$('#add').click(function(){$('form').toggle()});
		$(document).mouseup(function (e)
{
		var container = $("form");

		if (container.has(e.target).length === 0)
		{
			container.hide();
		}
});
	});
</script>
