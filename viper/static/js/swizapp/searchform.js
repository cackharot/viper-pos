(function($){
  
  $.fn.SearchForm = function() {
    var settings = $.extend({
      
    }, arguments[0]||{});
    
    $(this).each(function(){
      var f  = $(this);
      var id = f.attr('id');
      
      // Toggle tag cloud trigger
      f.find('.toggleTagCloud:first').bind('click', { form: f }, function(e){
        e.preventDefault();
        var btn = $(this);
        var img = btn.find('img');
        var frm = e.data.form;
        
        $.get(siwapp_urls.toggleTagCloud);
        btn.toggleClass('tags-selected');
        frm.parent().find('.tagselect').toggle();
        img.attr('src', img.attr('src').replace(/contract|expand/, btn.hasClass('tags-selected') ? 'contract' : 'expand'));
      });
      
      // Selectable tags
      f.parent().find('.tagselect:first span.tag')
        .SelectableTag({
          output: '#' + id + ' input[name=search[tags]]'
        });
      
      // Form reset button
      /*f.find('button[type=reset]:first').bind('click', { form: f }, function(e){
        //e.preventDefault();
        var frm = e.data.form;
        Tools.resetFields(frm);
        frm.parent().find('.tagselect span').removeClass('selected');
        frm.submit();
      });*/
      
      // Status filters
      f.find('ul.filters a.status').bind('click', { form: f }, function(e){
        e.preventDefault();
        var frm = e.data.form;
        var status = $(this).attr('class').match(/#(.*)#/).pop();
        frm.find('input[name=search[status]]').val(status);
        frm.submit();
      });
      
      // Quick Dates
      f.find('select[name=search_quick_dates]').bind('change', { form: f }, function(e){
        var frm = e.data.form;
        var val = $(this).val().toLowerCase();
        var mod, to, from;
        
        // function to get the monday date of the week
        function getMonday(d) {
          var day = d.getDay(),
              diff = d.getDate() - day + (day == 0 ? -6:1); // adjust when day is sunday
          return new Date(d.setDate(diff));
        }
        
        
        if (!val) {
            frm.find('input[name=fromDate]').val('');
            frm.find('input[name=toDate]').val('');
        } else {
          $('input[name=toDate]').datepicker('setDate', new Date());
          
          switch(val) {
            case 'last_week'    : mod = '-7';  break;
            case 'last_month'   : mod = '-1m'; break;
            case 'last_year'    : mod = '-1y'; break;
            case 'last_5_years' : mod = '-5y'; break;
            case 'this_week':
                mod = getMonday(new Date()); 
                break;
            case 'this_month':
                mod = new Date();
                mod.setDate(1);
                break;
            case 'this_year':
                mod = new Date();
                mod.setDate(1);
                mod.setMonth(0);
                break;
            default: 
                mod = null; 
                break;
          }
          
          $('input[name=fromDate]').datepicker('setDate', mod);
        }
      });
      
    });
  };
  
  $(function(){
    $('form.searchform').SearchForm();
  });
})(jQuery);



