<form action="/channels/{{channel.id}}/edit" method="POST">
<ul>
<li>Name: <input type="text" name = "title" class="url" value="{{channel.title}}"/></li>
<li>Url: <input type="text" name = "url" class="url" value="{{channel.url}}"/></li>
<li><input type="submit" value = "Save"></li>
</ul>
</form>
