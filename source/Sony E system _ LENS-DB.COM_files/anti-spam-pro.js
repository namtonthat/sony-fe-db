/*
Anti-spam Pro plugin
No spam in comments. No captcha.
codecanyon.net/item/antispam-pro/6491169
*/

(function($) {

	function anti_spam_pro_init() {
		var input_dynamic = '<input type="hidden" name="antispampro-q-'+antispampro_vars.input_name_suffix+'" class="antispampro-input-q" value="'+antispampro_vars.code+'" />';

		$('.antispampro-section').hide(); // hide inputs from users
		var answer = $('.antispampro-section-a input.antispampro-input-a:first').val(); // get answer (code)
		$('.antispampro-section-q input.antispampro-input-q').val(answer); // set answer (code) into other input instead of user
		$('.antispampro-section-e input.antispampro-input-e').val(''); // clear value of the empty input because some themes are adding some value for all inputs

		var comment_form_unique_hook_element = $('input[name=comment_post_ID]'); // unique comments form ID hook
		if ( comment_form_unique_hook_element.length !== 0 ) { // no comments form on this page (not single post or comments are disabled)
			var comment_form = $(comment_form_unique_hook_element).closest('form'); // get comments form
			if ( comment_form.length !== 0 ) {
				var antispampro_input = $(comment_form).find('input.antispampro-input-q');
				if ( antispampro_input.length == 0 ) { // anti-spam input does not exist (could be because of cache or because theme does not use 'comment_form' action)
					$(comment_form).append(input_dynamic); // add input using javascript
				}
			}
		}
	}

	$(document).ready(function() {
		anti_spam_pro_init();
	});

	$(document).ajaxSuccess(function() { // add support for comments forms loaded via ajax
		anti_spam_pro_init();
	});

})(jQuery);