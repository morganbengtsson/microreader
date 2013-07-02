<link rel="stylesheet" type="text/css" href="/static/style.css">

<form action="/channels/{{channel.id}}/edit" method="POST">
			

<ol class = "horizontal nav-section">
	<li>
		<a href = "/channels/{{channel.id}}/update" class= "update">
		<i class = "icon-arrow-circle"></i>
		Update
		</a>
	</li>	
	<li>
		<a href = "/channels/{{channel.id}}/delete" class = "delete">
			<i class = "icon-cross"></i>
			Delete
		</a>
	</li>
</ol>
				
<ul>
<li>
	<label for = "title">Name</label> 
	<input type="text" name = "title" class="url" value="{{channel.title}}"/>
</li>
<li>
	<label for = "url">Url</label> 
	<input type="text" name = "url" class="url" value="{{channel.url}}"/>
</li>
<li>
	<button type="submit">Save</button>
</li>
</ul>
</form>
