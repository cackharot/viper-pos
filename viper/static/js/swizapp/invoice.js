(function ($) {

	Contact = Backbone.RelationalModel.extend({
		idAttribute: 'Id',
		defaults: {
			CustomerId: null,
			FirstName: null,
			LastName: null,
			Email: null,
			Mobile: null,
			Phone: null,
			Address: null,
			Country: null,
			City: null,
		},
	});
		
	Customer = Backbone.RelationalModel.extend({
		idAttribute: 'Id',
		relations: [
            {
                type: Backbone.HasOne,
                key: 'Contact',
                relatedModel: 'Contact'
            }
        ],
		defaults: {
			CustomerNo: null,
			Contact: new Contact(),
			Status: true,
		},
		initialize: function(options){
			rivets.bind($('#customerDetails')[0], { model: this });
		},
	});
	
	LineItem = Backbone.RelationalModel.extend({
		idAttribute: 'Id',
		defaults: {
			OrderId: null,
			ProductId: null,
			Barcode: null,
			Name: null,
			Quantity: 0.0,
			MRP: 0.0,
			SellPrice: 0.0,
			Discount: 0.0,
			Amount: 0.0,
		},
		initialize: function(options) {
			this.bind('change:MRP', this.GetAmount, this)
			this.bind('change:Discount', this.GetAmount, this)
			this.bind('change:SellPrice', this.GetAmount, this)
			this.bind('change:Quantity', this.GetAmount, this)
		},
		GetAmount: function() {
			var amt = parseFloat(this.get('SellPrice')) * parseFloat(this.get('Quantity'))
			this.set('Amount',amt)
			return amt
		},
		validate: function(attrs) {
		    
		},
	});
	
	LineItemCollection = Backbone.Collection.extend({
		model: LineItem,
		GetTotalQuantity: function() {
			return this.reduce(function(m, x) {
				return (m + parseFloat(x.get('Quantity')));
			},0);
		},
		GetTotalAmount: function() {
			return this.reduce(function (m, x) {
				return m + x.GetAmount();
			}, 0);
		},
		GetActualAmount:function() {  
			return this.reduce(function (m, x) {
				return m + (parseFloat(x.get('MRP')) * parseFloat(x.get('Quantity')));
			}, 0); 
		},
	});
	
	OrderPayment = Backbone.RelationalModel.extend({
		idAttribute: 'Id',
		defaults: {
			OrderId: null,
			PaymentDate: new Date(),
			PaymentType: 'Cash',
			PaidAmount: 0.0,
			Description: null
		},
		validate: function(attrs) {
		    
		},
	});

	OrderPaymentsCollection = Backbone.Collection.extend({
		model: OrderPayment,
		GetPaidAmount: function () {
			return this.reduce(function (m, x) {
				return m + x.get('PaidAmount');
			}, 0);
		},
	});

	Order = Backbone.RelationalModel.extend({
		urlRoot: '/invoice/rest',
		idAttribute: 'Id',
		relations: [
            {
                type: Backbone.HasMany,
                key: 'LineItems',
                relatedModel: 'LineItem',
                collectionType: 'LineItemCollection',
            },
            {
                type: Backbone.HasMany,
                key: 'Payments',
                relatedModel: 'OrderPayment',
                collectionType: 'OrderPaymentsCollection',
            },
            {
                type: Backbone.HasOne,
                key: 'Customer',
                relatedModel: 'Customer'
            }
        ],
		initialize: function(options) {
			this.bind('add:LineItems',this.updateTotals,this)
			this.bind('remove:LineItems',this.updateTotals,this)
			
			this.bind('add:Payments', this.updateTotals,this)
			this.bind('remove:Payments', this.updateTotals,this)
		},
		defaults: {
			OrderNo: 0,
			OrderDate: new Date(),
			DueDate: null,
			CustomerId: null,
			//Customer: new Customer(),
			LineItems: new LineItemCollection,
			Payments: new OrderPaymentsCollection,
			TotalAmount: 0,
			ActualAmount: 0,
			PaidAmount: 0,
			BalanceAmount: 0,
			SavingsAmount: 0,
			TotalItems: 0,
			TotalQuantity: 0,
		},
		
		GetActualAmount: function() {  return this.get('LineItems').GetActualAmount(); },
		GetTotalAmount:  function() {  return this.get('LineItems').GetTotalAmount(); },
		GetPaidAmount:   function() {  return this.get('Payments').GetPaidAmount(); },
		
		GetBalanceAmount: function() { return this.GetTotalAmount() - this.GetPaidAmount(); },
		GetSavingsAmount: function() { return this.GetActualAmount() - this.GetTotalAmount(); },
		
		GetTotalQuantity: function() {  return this.get('LineItems').GetTotalQuantity(); },
		GetTotalItems: function() {  return this.get('LineItems').length; },
		
		updateTotals: function() {
			//console.log('Updating totals..')
			this.set('ActualAmount',this.GetActualAmount())
			this.set('TotalAmount',this.GetTotalAmount())
			this.set('PaidAmount',this.GetPaidAmount())
			
			this.set('BalanceAmount',this.GetBalanceAmount())
			this.set('SavingsAmount',this.GetSavingsAmount())
				
			this.set('TotalQuantity',this.GetTotalQuantity())
			this.set('TotalItems',this.GetTotalItems())
		},
		
		validate: function(attrs) {
		    
		},
	});
	
	
	LineItemCollectionView = Backbone.View.extend({
		el: $("#invoice-container"),
		template: _.template($('#tpl-lineitem').html()),
		multipleSelectItemTemplate: _.template($('#tpl-selectitem').html()),
		model: null,
		events: {
			"click #add-item": "addLineItem",
			"click a.del-lineitem": "deleteLineItem",
			"click #clear-lineitems": "clearLineItems",
			"keypress input[name=barcode]": "key_addlineitem",
			"keypress input[name=itemName]": "key_addlineitem",
		},
		initialize: function(options){
			this.vent = options.vent
			
			this.model.bind('add',this.addLineItemToDOM, this)
			this.model.bind('remove',this.removeLineItemFromDOM, this)
		},
		addLineItemToDOM: function(item){
			var data = item.toJSON()
			var html = this.template({ 'item': data })
			var h = $(html)[0]
						
			$('#tblInvoiceLineItems tbody').prepend(h)			
			rivets.bind(h, { model: item });
		},
		removeLineItemFromDOM: function(item){
			$("tr[data-id='" + item.get('Id') + "']", $('#tblInvoiceLineItems tbody')).remove()
		},
		render: function(){
			return this
		},
		addLineItem: function(e){
			var $txtBarcode = $('input[name=barcode]')
			var barcode = $txtBarcode.val()
			var quantity = 1.0
			
			if (barcode && barcode.length > 0 && barcode.length < 20) {
				var found = this.findAndUpdateItem(barcode, quantity)
				if (!found) {
					var that = this
					$.post('/sales/searchitem', {'barcode': barcode }, function (data) {
						if (data) {
							if (data.length > 1) {
								var tr = that.multipleSelectItemTemplate({'items': data})
								$('#tblSelectItem tbody').html(tr)

								$('#tblSelectItem tbody td button').each(function () {
									$(this).click(function () {
										var id = parseInt($(this).data('id'))
										data[id].Quantity = quantity
										that.addItemToUI(data[id], that)

										$('#tblSelectItem tbody').html('')
										$('#selectItemModal').modal('hide')
										
										$('input#itemName').val(data[id].Name)
										$('#barcode').focus()
									});
								});
								
								// show pop to select the item
								$('#selectItemModal').modal('show')
							} else {
								data[0].Quantity = quantity
								that.addItemToUI(data[0], that)
								$('input#itemName').val(data[0].Name)
								$('#barcode').focus()
							}
						} else {
							if (!isNaN(barcode)) {
								var mrp = parseFloat(barcode)
								if (mrp != 0.0 && mrp <= 1000.00) {
									var d = {}
									d.Barcode = mrp.toString()
									d.MRP = mrp
									d.SellPrice = mrp
									d.Quantity = 1.0
									d.Name = ''
									d.Discount = 0.0
									d.Id = uuid()
									that.addItemToUI(d, that)
								} else {
									showMsg('warn', '<strong>Oops!</strong> There are no items with barcode <span class="label label-info">' + barcode + '</span>.')
								}
							} else {
								showMsg('warn', '<strong>Oops!</strong> There are no items with barcode <span class="label label-info">' + barcode + '</span>.')
							}

							$('#barcode').focus()
						}
					});
				} else {
					$('#barcode').focus()
				}
			}else{
				showMsg('warn', '<strong>Enter a valid barcode!</strong>')
				$('#barcode').focus()
			}
		},
		deleteLineItem: function(e){
			e.preventDefault()			
			var tr = $(e.target)
			var itemid = tr.parent().parent().data('id')			
			var item = this.model.find(function (x) {
					return x.get('Id') == itemid;
			})				
			if(item)
				this.model.remove(item)
			return false
		},
		clearLineItems: function(e){
			e.preventDefault()
			this.model.reset()
			$('#tblInvoiceLineItems tbody tr').remove()
			this.invoice.updateTotals()
			return false
		},
		key_addlineitem: function (e) {
			if (e.keyCode == 13) { // enter key pressed
				this.addLineItem() 
			} else if( e.keyCode == 107 ) { // '+' key pressed
				this.addLineItem()
				e.preventDefault()
				e.stopPropagation()
			} else if( e.keyCode == 109 ) { // remove item if '-' pressed  
				
			}
		},
		findAndUpdateItem: function (barcode, quantity) {
			var item = this.model.find(function (x) {
				return x.get('Barcode') == barcode
			})
			if (item) {
				var q = parseFloat(item.get('Quantity'))
				item.set('Quantity', q + quantity)
				
				$('input#itemName').val(item.get('Name'))
				return true
			}
			return false
		},
		addItemToUI: function (data, that) {
			var item = new LineItem(data);
			that.model.add(item)
		},
	});
	
	window.InvoiceAppView = Backbone.View.extend({
		el: $("#invoice-container"),
		printTemplate   : _.template($('#templates script[rel="print"]:first').html()),
		checkouTemplate : _.template($('#tpl-chkoutorder').html()),
		model: new Order(),
		events: {
			"click #print-invoice": "printInvoice",
			"click #preview-invoice": "previewInvoice",			
			"click #payments-invoice": "paymentsInvoice",			
			"click #save-invoice": "saveInvoice",
		},
		initialize: function (options) {
			this.vent = options.vent
						
			var invoiceid = $('#invoiceid').val()
						
			this.editInvoice(invoiceid)
			
			//console.log(this.model)			
			
			this.LineItemCollectionsView = new LineItemCollectionView({ 
				model: this.model.get('LineItems'),
				vent: this.vent 
			})
			
			this.model.get('Payments').bind('change:PaidAmount', function(e) { this.model.updateTotals(); } ,this)
			this.model.get('LineItems').bind('change:Quantity change:MRP change:SellPrice change:Discount', function(e) { this.model.updateTotals(); } ,this)
			
			rivets.bind($('#invoiceDetails')[0], { model: this.model });
			rivets.bind($('#invoiceAmountDetails')[0], { model: this.model });
		},
		editInvoice: function(invoiceid) {
			if(invoiceid) {
				this.model.set('Id',invoiceid)
				this.model.fetch()
			} else {
				this.model.save()
			}
		},
		saveInvoice: function(e) {
			this.model.save({
				success: function(){
					showMsg('success', '#'+ this.model.get('OrderNo') + ' - Invoice saved successfully!')
				},
				error: function(){
					showMsg('warn','No Items added to the invoice. Cannot save invoice!')
				}
			})
		},
		printInvoice: function(){
			this.showPrintableOrder(function (w) {
				w.print()
				w.close()
			});
		},
		previewInvoice: function(){
			this.showPrintableOrder()
		},
		showPrintableOrder: function (callback) {
			var pw = window.open('', 'PrintInvoice', 'width=400,height=600,resizeable,scrollbars')
			pw.document.write(this.printTemplate({
				order: this.model
			}))
			pw.document.close()
			if (callback) callback(pw)
		},
		paymentsInvoice: function() {
			if (this.model.get('LineItems').length < 1) {
				showMsg('warn', '<strong>Oops!</strong> Invoice contains no items. Cannot <strong>process payment.</strong>', false)
				return
			}
			
			if (!this.model.get('CustomerId')) {
				showMsg('error', '<strong>Oops!</strong> Please enter a valid customer to save this order.')
				return
			}

			var orderamt = this.model.GetTotalAmount()
			var paidamt = this.model.GetPaidAmount()
			var balanceamt = paidamt > orderamt ? 0.0 : (orderamt - paidamt)
			
			this.model.set({'balanceamount': balanceamt})

			var html = this.checkouTemplate({
				'item': this.model
			})
			
			$('#checkoutOrderModel .modal-body').html(html)
			$('#checkoutOrderModel').modal('show')

			$('#checkoutOrderModel input[name="paidamount"]').select()
			$('#checkoutOrderModel #btnPayOrder').unbind('click', this.payOrder).click(this.payOrder)
		},
		payOrder: function () {
			var orderid = this.model.get('Id')
			var paidamount = Math.round(parseFloat($('#checkoutOrderModel input[name="paidamount"]').val().trim()))
			var paymenttype = $('#checkoutOrderModel select[name=paymenttype] option:selected').val().trim()
			var canprint = $('#checkoutOrderModel input[name=printTicket]').is(':checked')
			var oa = this.model.getOrderAmount()
			var pa = this.model.getPaidAmount()
			var orderamount = Math.round(oa)
			var prevpaidamt = Math.round(pa)

			if ((paymenttype == 'Cash' && (prevpaidamt + paidamount >= orderamount)) || (paymenttype == 'Credit' && paidamount < orderamount) || (paymenttype == 'Card' && paidamount > 0.0) || (paymenttype == 'Cheque' && paidamount > 0.0)) {
				
				if(paidamount > 0 && oa > orderamount) {
					paidamount += (oa-orderamount);//round off the less than 0.5 paise
				}
				
				this.model.set({
					'paidamount': prevpaidamt + paidamount,
					'isloaded': true,
					'isdirty': false,
				})

				var payment = new OrderPayment({
					'orderid': orderid,
					'paidamount': paidamount,
					'paymenttype': paymenttype,
					'paymentdate': new Date().toUTCString(),
				})

				this.model.get('payments').add(payment)
				this.model.save()
				
				showMsg('success', '<strong>Hooray!</strong> Payment Successfull &amp; <strong>#'+this.model.get('orderno')+'</strong> Invoice is saved.')
				
				this.vent.trigger('updateOrder', orderid)
				
				if(canprint)
					this.printOrder()
			} else if (paymenttype == 'Credit' && paidamount >= orderamount) {
				showMsg('warn', '<strong>Oops!</strong> Wrong Payment Type. Please choose <span class="label label-info">Cash</span> as payment type if the paid amount is greater than order amount.')
			} else {
				showMsg('warn', 'Paid amount should be greater than or equal to <strong>' + orderamount + '</strong>. Please choose <span class="label label-info">Credit</span> as payment type if the paid amount is lesser than order amount.')
			}
			
			$(this).unbind('click', this.payOrder)
			$('#checkoutOrderModel').modal('hide')
		},
	});
	
	rivets.configure({
	  prefix: 'rv',
	  preloadData: true,
      adapter: {
        subscribe: function(obj, keypath, callback) {
          obj.on('change:' + keypath, function(m, v) {
          	//console.log(m);
          	//console.log(v); 
          	callback(v); 
          });
        },
        read: function(obj, keypath) {
        	//console.log(keypath + ':' + obj.get(keypath));
        	
        	var keys = keypath.split('.');
        	var value = '';
        	
        	var o = obj;
        	
        	for(var i=0; i<keys.length; ++i) {
        		value = this.getValue(o,keys[i]);
        		//console.log(keys[i] + ':' + value);
        		o = value;
        	}
        	
          	return value || '';
        },
        getValue: function(obj,key){
        	return obj ?  obj.get(key) : '';
        },
        publish: function(obj, keypath, value) {
        	if(!isNaN(value)) {
        		value = parseFloat(value);
        	}
          	obj.set(keypath, value);
        }
      },
      formatters: {
        currency: function(value){
          return '<span class="currency">`</span> ' + (parseFloat(value) || 0.0).toFixed(2);
        },
        date: function(value){
          return !value ? '' : moment(value).format('MMMM DD, YYYY');
        },
        round: function(value) {
        	return Math.round(value);
        },
        fixed: function(value,prec) {
        	if(!prec)
        		prec = 2;
        	return value ? parseFloat(value).toFixed(prec) : 0.0;
        }
      }
    });
    
	var vent = _.extend({}, Backbone.Events)
	
	var salesappview = new InvoiceAppView({
		vent: vent
	})
	
	Mousetrap.bind(['f2'],function(e) {
		e.preventDefault()
		// quick search customer
	});
	
	Mousetrap.bind(['f5'],function(e) {
		e.preventDefault()
		$('#payments-invoice').trigger('click');
	});
		
	Mousetrap.bind(['f4'],function(e) {
		e.preventDefault()
		// quick add customer
	});
	
	Mousetrap.bind(['f6','f1'],function(e) {
		e.preventDefault()
		$('#barcode').focus();
	});
	
	Mousetrap.bind(['f11'],function(e) {
		e.preventDefault()
		$('#print-invoice').trigger('click');
	});
	
	Mousetrap.bind(['f12'],function(e) {
		e.preventDefault()
		$('#preview-invoice').trigger('click');
	});
	
	Mousetrap.bind('enter',function(e) {
		if($('#checkoutOrderModel').is(':visible')){
			e.preventDefault()
			$('#checkoutOrderModel #btnPayOrder').trigger('click')
		}
	});
	
})(jQuery);