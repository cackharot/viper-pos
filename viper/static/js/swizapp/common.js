$.fn.serializeObject = function()
{
	var o = {};
	var a = this.serializeArray();
	$.each(a, function() {
	    if (o[this.name] !== undefined) {
	        if (!o[this.name].push) {
	            o[this.name] = [o[this.name]];
	        }
	        o[this.name].push(this.value || '');
	    } else {
	        o[this.name] = this.value || '';
	    }
	});
	return o;
};

function ToLocalDate(inDate) {
	if (_.isString(inDate)) inDate = new Date(inDate);
	var date = new Date();
	date.setTime(inDate.valueOf() - 60000 * inDate.getTimezoneOffset());
	return date;
}
		
function hideMsg() {
	$('#statusMessage').fadeOut();
	$(document).trigger('NotificationRemoveEvent');
}

function showMsg(type, message, timeout) {
	$(document).trigger('NotificationEvent',
	{
		type: type,
		message: message
	});
}

function do_batch(action)
{
  var n = $('.listing input:checkbox[rel=item]:checked')
    .map(function(){ return $(this).val(); })
    .get();
  
  if (n && n.length) {
    switch(action) {
    	case 'delete':
    		if(window.swizapp.urls.delete){
    			window.location.href = window.swizapp.urls.delete + n;
    		}
    		break;
    	case 'print':
    		break;
    	case 'preview':
    		break;
    	case 'email':
    		break;
    }
  } else {
    showMsg('warn','No selection. Nothing to do.');
  }
}

(function($){
  
  // "select all" checkboxes should have rel="all"
  // "select this row" checkboxes should have rel="item"
  // Apply to table elements or it will throw an exception
  $.fn.selecTable = function(){
    var options = $.extend({
      classname: 'selected'
    }, arguments[0]||{});
    
    // Check/Unckeck all clicked: add/remove "selected" class to items
    $(this).find('input:checkbox[rel=all]').click(function(e){
      var t = $(this).closest('table');
      var tr = t.find('input:checkbox[rel=item]').closest('tr');
      t.find('input:checkbox[rel=item], input:checkbox[rel=all]').attr('checked', this.checked);
      if (this.checked)
        tr.addClass(options.classname);
      else
        tr.removeClass(options.classname);
    });
    
    // Check/Uncheck item clicked: add/remove "selected" class to it.
    $(this).find('input:checkbox[rel=item]').click(function(e){
      var t = $(this).closest('table');
      var tr = $(this).closest('tr');
      var n = t.find('input:checkbox[rel=item]:not(:checked)').length;
      t.find('input:checkbox[rel=all]').attr('checked', n == 0);
      if (this.checked)
        tr.addClass(options.classname);
      else
        tr.removeClass(options.classname);
    });
    
    return $(this);
  };
  
})(jQuery);

var tb = $('table.listing');
tb.selecTable();


// Apply to TR elements only
$.fn.rowClick = function(f){
    var options = $.extend({
      preventOn: 'a, button, input'
    }, arguments[1]||{});
    var tr = $(this).filter('tr');
    tr.click(f).find(options.preventOn).click(function(e){
    	//console.log(e.target) 
    	e.stopPropagation();
    	//e.preventDefault() 
    });
    return $(this);
};

$(function() {
	var showMsg = showMsg;
	var hideMsg = hideMsg;
	
	$(window).bind("unload", function() {$('button,a').die('click');});
	
	$(document).bind('AjaxRefreshEvent',function(e,data){
		if(window.swizapp.urls.edit)
		{
			var tr = $('table.listing:not(".noedit") tbody tr:not(".payments-row")');
			
			tr.rowClick(function() {
				var id = $(this).data('id');
				if (id)
		 			window.location.href =	window.swizapp.urls.edit + id;
			});
		}
	});
	$(document).trigger('AjaxRefreshEvent');
});

// ---------- SwizappFormTips------------------------------
/*
Adds a label tag with a 'tip' class before any element with an id and a title attributes and,
if wrapper tag provided, wraps both into a relative positioned tag. If not, their parent tag
is positioned relative. You can set not to position parent if you want. You can also change
default tip class name.

Options & defaults:
- wrapper   : null  (no wrapper)
- relative  : true  (parent will be positioned as 'relative')
- classname : 'tip' (label class name)
- test      : false (if true, sets a title for all items to test behavior)
- is_new    : false (if true, the form is not for editing db object)

<carlos@markhaus.com>
*/
$.fn.SwizappFormTips = function (options) {
	var parent, options = $.extend({
		wrapper: null,
		relative: true,
		classname: 'tip',
		test: false,
		is_new: false
	}, options || {});

	if (options.test) {
		this.attr('title', 'Lorem ipsum et dolor sit amet');
	}

	return this.each(function (i) {
		if (this.id && this.title) {
			if (options.wrapper) {
				parent = $(this).wrap('<' + options.wrapper.toLowerCase() + '></' + options.wrapper.toLowerCase() + '>').parent();
			} else {
				parent = $(this).parent();
			}

			if (options.relative) {
				parent.css('position', 'relative');
			}

			var label = $('<label id="' + this.id + '_label" for="' + this.id + '" class="tip" style="display:none;">' + this.title + '</label>');
			label.css({
				left: '0px',
				top: $(this).height() + 'px'
			});
			$(this).before(label);

			$(this).bind('focus', function (e) {
				//$(this).select(); // select text (to work also in textareas)
				$('#' + this.id + '_label').fadeIn('fast');
				if (options.is_new && $(this).val() == this.title) {
					$(this).val('');
				}
			}).bind('blur', function (e) {
				//$(this).val($(this).val()); // Unselect text (the same as before)
				$('#' + this.id + '_label').fadeOut('fast');
			});
		}
	});
};

Tools = {};

$(function(){
/*
  Resets all the <selector> descendants. Optionally you can pass as second argument
  a "not" selector to exclude items from the reset action.
  */
  Tools.resetFields = function(selector) {
    var not = arguments[1] || false;
    var items = $(selector).find(':text, :password, :checkbox, :image, :file');
    if (not)
      items = items.not(not);
    items.val(null);
  };
  
    /*
  Opens a popup window with the specified URL in it.
  As second argument you can set an object with the popup properties.
  */
  Tools.popup = function(url) {
    var settings = $.extend({
      name        : 'popup',
      width       : 960,
      height      : 700,
      menubar     : 'no',
      status      : 'no',
      location    : 'no',
      directories : 'no',
      copyhistory : 'no',
      scrollbars  : 'yes'
    }, arguments[1] || {});
    
    var options = [];
    for (key in settings)
      if (key != 'name')
        options.push(key + '=' + settings[key]);
    var w = window.open(url, settings.name, options.join(','));
    if (w && !w.closed)
      w.focus();
    return w;
  };
});

  /**
   * SelectableTag
   * Carlos Escribano Rey <carlos@markhaus.com>
   *
   * $('my_selector_to_get_all_tag_nodes').SelectableTag({
   *   output    : 'input_tag_id',
   *   classname : 'selected_status_CSS_class'
   * });
   *
   * <input type="hidden" id="tags" name="tags" value="" />
   * ...
   * <span class="tag">value1</span>
   * <span class="tag">value2</span>
   * ...
   * $('span.tag').SelectableTag();
   * ...
   *
   * If you click on tags with "value1" and "value2" values:
   * <input type="hidden" id="tags" name="tags" value="value1,value2" />
   * <span class="tag selected">value1</span>
   * <span class="tag selected">value2</span>
   */
  $.fn.SelectableTag = function() {
    var opt = $.extend({
      output    : '#tags',
      classname : 'selected'
    }, (arguments[0]||{}));

    $(this).click(function() {
      var r = $(opt.output);
      var t = $(this);
      var v = r.attr('value');

      if (t.toggleClass(opt.classname).hasClass(opt.classname)) {
        v = v + ',' + t.html();
      } else {
        v = v.replace(t.html(), '');
      }
      v = v.replace(/^,,*|,,*$/, '').replace(',,', ',');
      r.attr('value', v);
    });
  };
