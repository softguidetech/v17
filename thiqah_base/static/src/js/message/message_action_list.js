/** @odoo-module **/
import { ComposerTextInput } from '@mail/components/composer_text_input/composer_text_input';
import { patch } from 'web.utils';

patch(ComposerTextInput.prototype, 'mail/static/src/components/composer_text_input/composer_text_input.js', {

    //----------------------------------------------------------------------
    // Public
    //----------------------------------------------------------------------

    /**
     * @override
     */
     saveStateInStore() {
        this.composerView.composer.update({        
            textInputContent: this._getContent().replace(/[^\w\s\@\!\.\?\(\)]/gi, ''),
            // textInputContent: this._getContent(),
            textInputCursorEnd: this._getSelectionEnd(),
            textInputCursorStart: this._getSelectionStart(),
            textInputSelectionDirection: this._textareaRef.el.selectionDirection,
        });
    },

});




// odoo.define("thiqa_custom/static/src/js/message_action_list.js", function(require){
//     "use strict";

//     console.log('Hereee Odoo OWL')

//     const components = {
//         ComposerView: require("mail/static/src/models/composer_view/composer_view.js"),
//     };
  
//     const { patch } = require("web.utils");


//     patch(
//         components.ComposerView,
//         "thiqa_custom/static/src/js/message_action_list.js",
//         {
//           /**
//            * override
//            */
//            async updateMessage() {
            
//             const composer = this.composer;
            
//             if (!composer.textInputContent) {
//                 this.messageViewInEditing.messageActionList.update({ showDeleteConfirm: true });
//                 return;
//             }
//             const escapedAndCompactContent = escapeAndCompactTextContent(composer.textInputContent);

//             let body = escapedAndCompactContent.replace(/&nbsp;/g, ' ').trim();
//             body = body.replace(/[^\w\s\@]/gi, '')
            
//             body = this._generateMentionsLinks(body);
//             body = parseAndTransform(body, addLink);
//             body = this._generateEmojisOnHtml(body);
//             let data = {
//                 body: body,
//                 attachment_ids: composer.attachments.concat(this.messageViewInEditing.message.attachments).map(attachment => attachment.id),
//             };
//             try {
//                 composer.update({ isPostingMessage: true });
//                 const messageViewInEditing = this.messageViewInEditing;
//                 await messageViewInEditing.message.updateContent(data);
//                 if (messageViewInEditing.exists()) {
//                     messageViewInEditing.stopEditing();
//                 }
//             } finally {
//                 if (composer.exists()) {
//                     composer.update({ isPostingMessage: false });
//                 }
//             }
//         } 
//     }

//     );



// });