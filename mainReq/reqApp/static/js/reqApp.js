// -*- encoding: utf-8 -*-

// show or hide element content
function showHideContent(self, url, _elemType, _identifier, _registry, _canEdit){// _registry = 0      _canEdit= 0
    var content = $(self).parent().parent().parent().next('div[name=element_content]');
    if(content.css('display') == 'block'){
        content.hide('slow');
    }else{
        if(content.attr("ready") == 'no'){
            content.attr("ready",'yes');
            $.get(url,{identifier:_identifier, elemType:_elemType, registry:_registry, canEdit:_canEdit},function(data){
                content.html(data);
            });
        }
        content.show('slow');
    }
}

// open all elements content
function showContents(){
    $('[name=element_content]').hide();
    $('[trigger=yes]').click();
}

// close all elements content
function hideContents(){
    $('[name=element_content]').hide('slow');
}

// reload after canceling element edition
function cancelElementEdition(identifierText){
    //location.reload(true); // WARNING: not use! (problems with 'resend form')
    //window.location = window.location.href.split("#")[0];
    $('#'+identifierText+'_form').hide('slow');
    $('#'+identifierText).show('slow');
}

// show edition element from
function editElement(identifierText, url, _identifier, _elemType){
    $.get(url,{getForm:"yes", identifier:_identifier, elemType:_elemType},function(data){
        $('#'+_identifier+'_formdiv').html(data);
        $('#'+identifierText+'_form').show('slow');
        loadDateTimePicker();
    });
    $('#'+identifierText).hide('slow');
}

// cancel new element edition (reload view)
function cancelNewElement(){
    //location.reload(true); // WARNING: not use! (problems with 'resend form')
    //window.location = window.location.href.split("#")[0];
    $('#newElementForm').hide('slow');
}

// edit new element form
function editNewElement(){
    $('#newElementForm').show();
}

// delete element from list
function deleteElement(idText, identifier, csrf, deleteWarning){
    // confirm action
    if(!confirm("¿Desea eliminar "+idText+" de la lista?\n\n"+deleteWarning+"\n\n* Precaución: Elementos asociados se deben eliminar manualmente."))
        return;

    var deletionReason = prompt("Explique en pocas palabras el motivo de esta eliminación:", "Este elemento es eliminado porque...");
    if(deletionReason == null)
        return;
    if(deletionReason == "")
        deletionReason = "( MOTIVO NO ESPECIFICADO! )";

    var params = new Array();
    params["csrfmiddlewaretoken"] = csrf;// '{{csrf_token}}'
    params["identifier"] = identifier;
    params["delete"] = "delete";
    params["deletionReason"] = deletionReason;
    
    post_to_url("", params, "post");
}

// edit form validation ajax
function validEditionForm(event,button){
    event = event || window.event; // cross browser
    event.preventDefault(); // avoid reload
    
    var updateReason = prompt("Explique en pocas palabras el motivo de esta modificación:", "Este elemento es modificado porque...");
    if(updateReason == null){
        return false;
    }
    $(button).next('[name=updateReason]').val(updateReason);
    return validForm(event,button);
}

// form validation ajax
function validForm(event,button){
    var form = button.form;
    button.disabled = true;

    event = event || window.event; // cross browser
    event.preventDefault(); // avoid reload

    // put ajax mark
    var input = document.createElement("input");
    input.type = "hidden";
    input.name = "validate";
    input.value = '1';
    form.appendChild(input);
    
    $.ajax({
        url: "",
        data: $(form).serialize(),
        type: "POST",
        dataType: 'json',
        success: function(data){
            if(data.server_response == "OK"){
                // remove ajax mark
                form.removeChild(input);
                
                // send form
                form.submit();
            }else{
                // remove ajax mark
                form.removeChild(input);
                button.disabled = false;
                
                // clean previous errors
                $('.invalid').removeClass('invalid').prev().hide();
                
                // show form errors
                for(var e = 0; e < data.errors.length; e++){
                    input_name = data.errors[e][0];
                    input_error = data.errors[e][1];
                    var field = form.elements[input_name];
                    if(field!=undefined){
                        field.className += " invalid";
                        var newInput = $("<div style='color:Red'>"+input_error+"</div>");
                        $(field).before(newInput);
                    }
                }
            }
       },
       error: function(jqXHR, textStatus, errorThrown){
           alert("ERROR: Este elemento ha sido eliminado previamente. Por favor recarga la página.");
       }
    });
    
    // avoid reload
    return false;
}

// js create & send post form
function post_to_url(path, params, method) {
    //var params = new Array(); params["file"] = 'test.pdf';
    method = method || "post"; // Set method to post by default if not specified.

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
         }
    }

    document.body.appendChild(form);
    form.submit();
}


/* tinymce add image */
function addMCEImg(src){
    var ed = tinymce.EditorManager.activeEditor, args = {}, el;

	if (src === '') {
		if (ed.selection.getNode().nodeName == 'IMG') {
			ed.dom.remove(ed.selection.getNode());
			ed.execCommand('mceRepaint');
		}
		return;
	}

	if (!ed.settings.inline_styles) {
		args = tinymce.extend(args, {
		});
	} else
		args.style = this.styleVal;

	tinymce.extend(args, {
		src : src.replace(/ /g, '%20'),
		alt : "ERROR_IMG_NOT_FOUND: " + src.replace(/ /g, '%20'),
		//width : 100, // set default size??
		//height : 100 // set default size??
	});

	el = ed.selection.getNode();

	if (el && el.nodeName == 'IMG') {
		ed.dom.setAttribs(el, args);
		ed.execCommand('mceRepaint');
		ed.focus();
	} else {
		tinymce.each(args, function(value, name) {
			if (value === "") {
				delete args[name];
			}
		});

		ed.execCommand('mceInsertContent', false, ed.dom.createHTML('img', args), {skip_undo : 1});
		ed.undoManager.add();
	}
}

// tinymce insert img
function insertMceImg(input,url,csrf,host){
    var file = input.files[0];
    var fd = new FormData();		        
    fd.append('file', file);
    fd.append('csrfmiddlewaretoken', csrf);
    
    $.ajax({
        url: url,
        data: fd,
        type: "POST",
        cache: false,
	    contentType: false,
	    processData: false,
        success: function(data){
            if(data != ""){
                addMCEImg(data, host);//host --> "http://localhost:8000"
            }else{
                alert('ERROR: archivo de imagen inválido!');
            }
       }
    });
}

// add img by url prompt
function promptImgURL(){
    if(!imgAlignMessage())
        return;
    var url = prompt("Insert Image By URL:", "http://anakena.dcc.uchile.cl/anakena.jpg");
    if (url!=null) {
        addMCEImg(url);
    }
}

// image align confirm message
function imgAlignMessage(){
    return confirm("¡PRECAUCIÓN!\n\nPara CENTRAR o ALINEAR la imagen, primero debe alinear el cursor del editor.\nDe otra manera la imagen sólo se mostrará alineada a la izquierda en el Documento PDF.\n\n¿Desea insertar una imagen en la posición actual del cursor?");
}

// alarms modals
function prepareModals(){
    $('[name=reqAppModal]').each(function(i){
        var itsModal = $(this);
        $(this).next().click(function(){itsModal.modal('show');});
        $(this).modal({
            show:false,
        });
    });
}
function alarmsBlink(){
    $('[blink=yes]').each(function(i){
        var alarm = $(this);
        var container = $(this).parent().parent().parent().parent();
        
        var backgroundColor = alarm.css('background-color');
        var color = alarm.css('color');
        
        function reqBlink(){
            var count = alarm.attr("blinking");
            if(count <= 0){
                return;
            }
            
            alarm.attr("blinking",(count-1));
            
            alarm.animate({
                'background-color':color,
                'color':backgroundColor,
            },300).animate({
                'background-color':backgroundColor,
                'color':color,
            },300, reqBlink);
        }
        
        container.hover(function(){
            alarm.attr("blinking",10);
            reqBlink();
        },function(){
            alarm.attr("blinking",-1);
        });
    });
}
function prepareAlarms(){
    prepareModals();
    alarmsBlink();
}
$(window).load(function(){
    prepareAlarms();
});

// tasks buttons
function taskButton(confirmText, id, nextTaskState, csrf){
    // confirm action
    if(!confirm(confirmText))
        return;

    var params = new Array();
    params["csrfmiddlewaretoken"] = csrf;// '{{csrf_token}}'
    params["id"] = id;
    params["nextTaskState"] = nextTaskState;
    
    post_to_url("", params, "post");
}

// tasks countdown
$(window).bind("load", function(){
    $('[name=countDown]').each(function(i){
        var secondsToDeadline = $(this).attr("secondsToDeadline");
        if(secondsToDeadline > 0){
            $(this).countdown({
                until: new Date(+new Date() + (secondsToDeadline * 1000)),
                compact: true, 
                layout: 'Tiempo restante: {dn}d {hnn}{sep}{mnn}{sep}{snn}',
            });
        }
    });
});

// datetime picker
// <input datetimepicker='yes' type="text" >
function loadDateTimePicker(){
    var mydatetimepicker = $('[datetimepicker=yes]');
    mydatetimepicker.datetimepicker({format:'Y-m-d H:i',step:10});
    mydatetimepicker.attr('datetimepicker','no');
}
$(window).bind("load", function(){
    loadDateTimePicker();
});


// elements filter
function filterThis(getParams){
    var filterQuery = "";
    $('[name=filterSelect]').each(function(i){filterQuery = filterQuery + $(this).val();});
    location = "?filter=true" + filterQuery + getParams;
}

// capture Ctrl+f and F3 for word search
window.addEventListener("keydown",function (e) {
    if (e.keyCode === 114 || (e.ctrlKey && e.keyCode === 70)) { 
        showContents();
    }
})

// toolips
function prepareTooltips(){
    $('[data-toggle=tooltip]').tooltip();
}
$(window).bind("load", function(){
    prepareTooltips();
});

// matrices
$(window).bind("load", function() {
    var selected = "none";
    function animateSelectedElements(self){
        self.hide();
        self.show('slow');
    }
    
    $('[name=matrix_element]').click(function(){
        var el = $(this);
        var imSecond = false;
        var mtType = $('#matr').attr('matrixType');
        
        if(selected != "none"){
            selected.hide();
            $('th[elRowIdentifier='+selected.parent().attr('elRowIdentifier')+']').css({'border-color': 'rgba(0,0,0,0)',});
            $('th[elColIdentifier='+selected.parent().attr('elColIdentifier')+']').css({'border-color': 'rgba(0,0,0,0)',});
        }
        selected = el.children('.matr_selec').show();
        $('th[elRowIdentifier='+selected.parent().attr('elRowIdentifier')+']').css({'border': '1px solid Blue',});
        $('th[elColIdentifier='+selected.parent().attr('elColIdentifier')+']').css({'border': '1px solid Blue',});
        
        $.get("",{getElement:true, matrixType:mtType, elType:"1", identifier:el.attr('elRowIdentifier')},function(data){
            var row = $('#row');
           row.html(data);
           animateSelectedElements(row);
            if(imSecond){
                prepareAlarms();
                prepareTooltips();
                location = "#bottom";
            }else{
                imSecond = true;
            }
        });
        
        $.get("",{getElement:true, matrixType:mtType, elType:"2", identifier:el.attr('elColIdentifier')},function(data){
            var col = $('#col');
            col.html(data);
            animateSelectedElements(col);
            if(imSecond){
                prepareAlarms();
                prepareTooltips();
                location = "#bottom";
            }else{
                imSecond = true;
            }
        });
    });

    $('[name=matrix_element]').hover(function() {
        $('th[elRowIdentifier='+$(this).attr('elRowIdentifier')+']').css({'background-color': 'Gold',});
        $('th[elColIdentifier='+$(this).attr('elColIdentifier')+']').css({'background-color': 'Gold',});
        //$('th[elRowIdentifier='+$(this).attr('elRowIdentifier')+']').css({'border': '1px solid Black',});
        //$('th[elColIdentifier='+$(this).attr('elColIdentifier')+']').css({'border': '1px solid Black',});
    }, function() {
        $('th[elRowIdentifier='+$(this).attr('elRowIdentifier')+']').css({'background-color': 'rgba(0,0,0,0)',});
        $('th[elColIdentifier='+$(this).attr('elColIdentifier')+']').css({'background-color': 'rgba(0,0,0,0)',});
        //$('th[elRowIdentifier='+$(this).attr('elRowIdentifier')+']').css({'border-color': 'rgba(0,0,0,0)',});
        //$('th[elColIdentifier='+$(this).attr('elColIdentifier')+']').css({'border-color': 'rgba(0,0,0,0)',});
    });
});

// Nprogress bar --> https://github.com/rstacruz/nprogress
function prepareNProgressBar(){
    NProgress.configure({
        minimum:0.1,
        showSpinner:false,
        trickleRate:0.2,
        trickleSpeed:800,
    });
    $('a[progressbar]').click(function(){
        NProgress.start();
    });
    $('button[progressbar]').click(function(){
        NProgress.start();
    });
    $('select[progressbar]').change(function(){
        NProgress.start();
    });
}
$(window).bind("load", function(){
    prepareNProgressBar();
});
$(window).unload(function(){
    NProgress.done();
});
